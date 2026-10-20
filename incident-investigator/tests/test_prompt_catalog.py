from __future__ import annotations

from app.models import AgentRole
from app.prompts import prompt_metadata, prompt_spec


def test_runtime_prompt_catalog_has_one_exact_version_for_each_operation() -> None:
    expected = {
        (AgentRole.D1, "plan"): ("incident-investigator-d1-orchestrator", "v3"),
        (AgentRole.D3, "investigate"): ("incident-investigator-d3-observability", "v2"),
        (AgentRole.D4, "investigate"): ("incident-investigator-d4-code-deploy", "v2"),
        (AgentRole.D5, "investigate"): ("incident-investigator-d5-data", "v2"),
        (AgentRole.D6, "investigate"): ("incident-investigator-d6-ai-behavior", "v2"),
        (AgentRole.D7, "review"): ("incident-investigator-d7-critic", "v1"),
        (AgentRole.D7, "review_report"): ("incident-investigator-d7-report-review", "v2"),
        (AgentRole.D8, "write"): ("incident-investigator-d8-reporter", "v1"),
    }
    for (role, operation), (identifier, version) in expected.items():
        spec = prompt_spec(role, operation)
        metadata = prompt_metadata(role, operation)
        assert (spec.identifier, spec.version) == (identifier, version)
        assert metadata["prompt_identifier"] == identifier
        assert metadata["prompt_version"] == version
        assert len(metadata["prompt_sha256"]) == 64
