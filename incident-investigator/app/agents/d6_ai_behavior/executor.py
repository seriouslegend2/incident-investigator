from __future__ import annotations

import uuid

from ...models import AgentFinding, AgentRole
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime
from ..tool_execution import run_required_tool_then_structure, validate_evidence_citations
from .models import D6Analysis, D6InvestigateOutput
from .tools import build_tools


async def build_d6(invocation: AgentInvocation, runtime: AgentRuntime) -> D6InvestigateOutput:
    if invocation.task is None:
        raise ValueError("D6 requires a scoped task")
    tools = build_tools(invocation, runtime)
    analysis, evidence = await run_required_tool_then_structure(
        runtime=runtime,
        invocation=invocation,
        system_prompt=(await runtime.resolve_prompt(AgentRole.D6, "investigate")).system_message,
        user_prompt=f"Complaint: {invocation.case.complaint}\nTask: {invocation.task.question}\nWhy: {invocation.task.reason}",
        tools=tools,
        output_model=D6Analysis,
        role=AgentRole.D6,
        operation="investigate",
        max_tool_calls=4,
    )
    validate_evidence_citations(analysis.evidence_ids, evidence)
    return D6InvestigateOutput(
        finding=AgentFinding(
            finding_id=f"finding_{uuid.uuid4().hex}",
            role=AgentRole.D6,
            answer=analysis.answer,
            observations=analysis.observations,
            evidence_ids=analysis.evidence_ids,
            limitations=analysis.limitations,
        )
    )
