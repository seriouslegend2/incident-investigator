"""Offline contract checks only; no models, repositories, databases or clouds queried."""
import copy
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


schema = read("agent-io.schema.json")
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)
receipt_schema = read("tool-receipt.schema.json")
Draft202012Validator.check_schema(receipt_schema)
registry = read("tool-contracts.json")
roles = {"D1", "D3", "D4", "D5", "D6", "D7", "D8"}
checked = 0
for role in sorted(roles):
    fixture = read(f"{role.lower()}-example.json")
    for kind in ("task", "answer", "result"):
        validator.validate(fixture[kind])
        checked += 1
    assert fixture["task"]["agent_id"] == fixture["answer"]["agent_id"]
    assert fixture["result"]["answer"] == fixture["answer"]
    if role == "D1":
        assert not fixture["task"]["known_premises"]
        assert not fixture["task"]["scope"]["entity_refs"]
    if role == "D5":
        assert fixture["task"]["knowledge"]["read_contract_refs"]
        assert fixture["task"]["knowledge"]["excerpts"]
        assert fixture["answer"]["execution_status"] == "partial"
        assert not fixture["answer"]["data_findings"]["temporal_basis"]["historical_state_established"]

validator.validate(read("failed-result-example.json"))
checked += 1

names = set()
for tool in registry["tools"]:
    assert tool["name"] not in names
    names.add(tool["name"])
    assert set(tool["agents"]) <= roles
    assert "D2" not in tool["agents"]
    for field in ("input_schema", "data_schema"):
        wrapped = {"$schema": schema["$schema"], **tool[field], "$defs": registry["$defs"]}
        Draft202012Validator.check_schema(wrapped)
        checked += 1
    if tool["name"] in {"delegate_task", "request_clarification"}:
        assert tool["agents"] == ["D1"]
    if "D8" in tool["agents"]:
        assert tool["name"] in {"case.read", "evidence.fetch", "report.store_draft"}
    if tool["name"].startswith(("code.", "data.", "deploy.", "telemetry.", "ai.")):
        assert "write" not in tool["name"]

by_name = {tool["name"]: tool for tool in registry["tools"]}
receipt_validator = Draft202012Validator(receipt_schema)
for stage in read("tool-flow-example.json")["stages"]:
    tool = by_name[stage["request"]["tool"]]
    Draft202012Validator({**tool["input_schema"], "$defs": registry["$defs"]}).validate(stage["request"]["arguments"])
    receipt_validator.validate(stage["response"])
    checked += 2
    if stage["response"]["data"] is not None:
        Draft202012Validator({**tool["data_schema"], "$defs": registry["$defs"]}).validate(stage["response"]["data"])
        checked += 1


def reject(candidate, why):
    if validator.is_valid(candidate):
        raise AssertionError(f"Invalid fixture accepted: {why}")


negative = 0
d5 = read("d5-example.json")
candidate = copy.deepcopy(d5["answer"])
candidate["agent_id"] = "D2"
reject(candidate, "removed agent")
negative += 1
candidate = read("failed-result-example.json")
candidate["answer_state"] = "valid"
reject(candidate, "valid result requires an actual model answer")
negative += 1
candidate = copy.deepcopy(d5["answer"])
candidate["cost"] = {"elapsed_ms": 1}
reject(candidate, "LLM cannot mint runtime costs")
negative += 1
candidate = copy.deepcopy(d5["answer"])
candidate["observations"][0]["evidence_refs"] = []
reject(candidate, "source-free observation")
negative += 1
candidate = copy.deepcopy(d5["task"])
del candidate["knowledge"]
reject(candidate, "missing shared-knowledge handoff")
negative += 1
candidate = read("d7-example.json")["answer"]
candidate["review"]["target"]["kind"] = "report"
reject(candidate, "report approval without exact artifact identity/hash")
negative += 1
candidate = read("d8-example.json")["answer"]
candidate["report_draft"]["approved"] = True
reject(candidate, "writer cannot self-approve")
negative += 1
read_tool = next(t for t in registry["tools"] if t["name"] == "data.read_bounded")
read_validator = Draft202012Validator({**read_tool["input_schema"], "$defs": registry["$defs"]})
assert not read_validator.is_valid({"sql": "UPDATE production SET value=1"})
negative += 1

# Documentation must expose every eligible tool and full per-role fixture link.
doc_names = {"D1": "d1-investigation-lead", "D3": "d3-observability", "D4": "d4-code-deployment", "D5": "d5-data", "D6": "d6-ai-behavior", "D7": "d7-critic", "D8": "d8-report-writer"}
for role, filename in doc_names.items():
    prose = (ROOT.parent / "agents" / f"{filename}.md").read_text()
    assert f"{role.lower()}-example.json" in prose, filename
    for tool in registry["tools"]:
        if role in tool["agents"]:
            assert f"`{tool['name']}`" in prose, (filename, tool["name"])
    blocks = [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", prose, re.S)]
    assert len(blocks) == 2, filename
    task_variant = next(v for v in schema["$defs"]["Task"]["oneOf"] if v["properties"]["agent_id"]["const"] == role)
    answer_variant = next(v for v in schema["$defs"]["AgentAnswer"]["oneOf"] if v["properties"]["agent_id"]["const"] == role)
    extension_name = next(key for key in answer_variant["properties"] if key not in {"agent_id", "execution_status", "observations", "interpretations", "unknowns", "coverage_receipt_refs", "suggested_followups"})
    for block, subschema in zip(blocks, [task_variant["properties"]["role_input"], answer_variant["properties"][extension_name]]):
        Draft202012Validator({**subschema, "$defs": schema["$defs"]}).validate(block)
        checked += 1

protocol = (ROOT.parent / "agent-protocol.md").read_text()
for block in re.findall(r"```json\n(.*?)\n```", protocol, re.S):
    validator.validate(json.loads(block))
    checked += 1

print(f"PASS: {checked} schema/example checks; {len(names)} tools; 7 role documents; {negative} invalid cases rejected.")
print("These checks validate documentation contracts, not runtime behavior, causal accuracy or production safety.")
