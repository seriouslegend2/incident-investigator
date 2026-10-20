from __future__ import annotations

import uuid

from ...models import AgentFinding, AgentRole
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime
from ..tool_execution import run_required_tool_then_structure, validate_evidence_citations
from .models import D5Analysis, D5InvestigateOutput
from .tools import build_tools


async def build_d5(invocation: AgentInvocation, runtime: AgentRuntime) -> D5InvestigateOutput:
    if invocation.task is None or invocation.read_contract is None:
        raise ValueError("D5 requires both a scoped task and D4 ReadContract")
    tools = build_tools(invocation, runtime)
    contract = invocation.read_contract
    analysis, evidence = await run_required_tool_then_structure(
        runtime=runtime,
        invocation=invocation,
        system_prompt=(await runtime.resolve_prompt(AgentRole.D5, "investigate")).system_message,
        user_prompt=(
            f"Complaint: {invocation.case.complaint}\nTask: {invocation.task.question}\n"
            f"Authorized contract: relation={contract.relation}, lookup={contract.lookup_field}:"
            f"{contract.lookup_value}; reason={contract.reason}"
        ),
        tools=tools,
        output_model=D5Analysis,
        role=AgentRole.D5,
        operation="investigate",
        max_tool_calls=3,
    )
    validate_evidence_citations(analysis.evidence_ids, evidence)
    return D5InvestigateOutput(
        finding=AgentFinding(
            finding_id=f"finding_{uuid.uuid4().hex}",
            role=AgentRole.D5,
            answer=analysis.answer,
            observations=analysis.observations,
            evidence_ids=analysis.evidence_ids,
            limitations=analysis.limitations,
        )
    )
