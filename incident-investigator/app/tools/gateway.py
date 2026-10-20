from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

from langchain_core.tools import BaseTool, StructuredTool
from langsmith.run_helpers import trace

from ..agents.contracts import AgentInvocation
from ..db.repository import IncidentRepository
from ..models import AgentRole, EvidenceRecord, ReadContract
from .contracts import EvidenceSearchInput, EvidenceSearchOutput
from .local_code import LocalCodeSearch

ROLE_SOURCE_KIND = {
    AgentRole.D3: "observability",
    AgentRole.D4: "code_deploy",
    AgentRole.D5: "data",
    AgentRole.D6: "ai_runtime",
}


@dataclass(frozen=True)
class ToolGateway:
    """Policy boundary: one trusted case scope and one source kind per role/tool."""

    repository: IncidentRepository
    max_rows: int
    local_code: LocalCodeSearch | None = None

    async def search(
        self,
        *,
        invocation: AgentInvocation,
        role: AgentRole,
        source_kind: str,
        tool_name: str,
        query: str,
        read_contract: ReadContract | None = None,
        backend: str = "supabase",
    ) -> EvidenceSearchOutput:
        if ROLE_SOURCE_KIND.get(role) != source_kind:
            raise PermissionError(f"{role.value} cannot read {source_kind}")
        if source_kind == "data" and read_contract is None:
            raise PermissionError("D5 data access requires a D4-backed ReadContract")

        tool_call_id = f"tool_{uuid.uuid4().hex}"
        arguments = {"query": query}
        if read_contract is not None:
            arguments["read_contract_id"] = read_contract.contract_id
            arguments["relation"] = read_contract.relation

        try:
            # This child span makes the actual bounded source read visible below
            # the agent that requested it. It contains query/result metadata,
            # never connector credentials or arbitrary source access.
            async with trace(
                name=f"tool/{role.value.lower()}/{tool_name}",
                run_type="tool",
                inputs={
                    "tool": tool_name,
                    "source_kind": source_kind,
                    "query": query,
                    "authorized_scenario": invocation.case.scope.scenario_id,
                    "read_contract": arguments.get("read_contract_id"),
                },
                tags=["incident-investigator", "tool", role.value.lower(), source_kind],
                metadata={
                    "case_id": invocation.case.case_id,
                    "agent_run_id": invocation.run_id,
                    "task_id": invocation.task_id,
                    "tool_call_id": tool_call_id,
                },
            ) as tool_run:
                if backend == "local_code":
                    if source_kind != "code_deploy" or self.local_code is None:
                        raise PermissionError("local code access is available only to D4")
                    rows = await self.local_code.search(query, limit=self.max_rows)
                elif backend == "contract_description":
                    if source_kind != "data" or read_contract is None:
                        raise PermissionError("contract description requires D5 ReadContract")
                    rows = [
                        {
                            "source_record_id": f"contract:{read_contract.contract_id}",
                            "observed_at": invocation.case.created_at,
                            "summary": "Backend-authorized data projection",
                            "content": (
                                f"relation={read_contract.relation} "
                                f"lookup_field={read_contract.lookup_field} "
                                f"lookup_value={read_contract.lookup_value}"
                            ),
                            "coverage_note": (
                                "backend policy permits only this bounded demo relation and lookup; "
                                "no schema discovery or arbitrary SQL is available"
                            ),
                            "metadata": {"contract_id": read_contract.contract_id},
                        }
                    ]
                else:
                    rows = await self.repository.search_demo_source(
                        scenario_id=invocation.case.scope.scenario_id,
                        source_kind=source_kind,
                        query=query,
                        limit=self.max_rows,
                    )
                if read_contract is not None:
                    relation_marker = f"relation={read_contract.relation}"
                    rows = [row for row in rows if relation_marker in row["content"]]
                records = []
                for row in rows:
                    raw_metadata = row.get("metadata", {})
                    metadata = (
                        json.loads(raw_metadata) if isinstance(raw_metadata, str) else raw_metadata
                    )
                    records.append(
                        EvidenceRecord(
                            evidence_id=f"ev_{uuid.uuid4().hex}",
                            source_kind=source_kind,  # type: ignore[arg-type]
                            source_record_id=row["source_record_id"],
                            observed_at=row["observed_at"],
                            summary=row["summary"],
                            coverage_note=row["coverage_note"],
                            content=row["content"],
                            metadata={
                                str(key): str(value) for key, value in (metadata or {}).items()
                            },
                        )
                    )
                await self.repository.record_tool_call(
                    tool_call_id=tool_call_id,
                    case_id=invocation.case.case_id,
                    task_id=invocation.task_id,
                    run_id=invocation.run_id,
                    role=role,
                    tool_name=tool_name,
                    arguments=arguments,
                    status="succeeded",
                    result_count=len(records),
                )
                for record in records:
                    await self.repository.record_evidence(
                        record,
                        case_id=invocation.case.case_id,
                        tool_call_id=tool_call_id,
                    )
                result = EvidenceSearchOutput(
                    evidence=records,
                    result_count=len(records),
                    coverage_note=(
                        f"Searched demo {source_kind} records within trusted scenario "
                        f"{invocation.case.scope.scenario_id}; maximum {self.max_rows} rows."
                    ),
                )
                tool_run.end(
                    outputs={
                        "result_count": result.result_count,
                        "evidence_ids": [record.evidence_id for record in records],
                        "source_record_ids": [record.source_record_id for record in records],
                        "coverage_note": result.coverage_note,
                    }
                )
                return result
        except Exception:
            await self.repository.record_tool_call(
                tool_call_id=tool_call_id,
                case_id=invocation.case.case_id,
                task_id=invocation.task_id,
                run_id=invocation.run_id,
                role=role,
                tool_name=tool_name,
                arguments=arguments,
                status="failed",
                result_count=0,
            )
            raise


def make_evidence_tool(
    *,
    name: str,
    description: str,
    gateway: ToolGateway,
    invocation: AgentInvocation,
    role: AgentRole,
    source_kind: str,
    read_contract: ReadContract | None = None,
    backend: str = "supabase",
) -> BaseTool:
    """Create a case-scoped tool; models cannot send a source ID, tenant or database target."""

    async def search_evidence(query: str) -> str:
        result = await gateway.search(
            invocation=invocation,
            role=role,
            source_kind=source_kind,
            tool_name=name,
            query=query,
            read_contract=read_contract,
            backend=backend,
        )
        return json.dumps(result.model_dump(mode="json"))

    return StructuredTool.from_function(
        coroutine=search_evidence,
        name=name,
        description=description,
        args_schema=EvidenceSearchInput,
    )
