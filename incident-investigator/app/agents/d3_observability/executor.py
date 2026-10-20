from __future__ import annotations

import uuid

from ...models import AgentFinding, AgentRole
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime
from ..tool_execution import run_required_tool_then_structure, validate_evidence_citations
from .models import D3Analysis, D3InvestigateOutput
from .prompt import SYSTEM_PROMPT
from .tools import build_tools


async def build_d3(invocation: AgentInvocation, runtime: AgentRuntime) -> D3InvestigateOutput:
    if invocation.task is None:
        raise ValueError("D3 requires a scoped task")
    tools = build_tools(invocation, runtime)
    analysis, evidence = await run_required_tool_then_structure(
        runtime=runtime,
        invocation=invocation,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Complaint: {invocation.case.complaint}\nTask: {invocation.task.question}\nWhy: {invocation.task.reason}",
        tools=tools,
        output_model=D3Analysis,
        role=AgentRole.D3,
        operation="investigate",
        max_tool_calls=3,
    )
    validate_evidence_citations(analysis.evidence_ids, evidence)
    return D3InvestigateOutput(
        finding=AgentFinding(
            finding_id=f"finding_{uuid.uuid4().hex}",
            role=AgentRole.D3,
            answer=analysis.answer,
            observations=analysis.observations,
            evidence_ids=analysis.evidence_ids,
            limitations=analysis.limitations,
        )
    )
