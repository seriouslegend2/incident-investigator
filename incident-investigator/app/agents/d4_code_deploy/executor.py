from __future__ import annotations

import uuid

from ...models import AgentFinding, AgentRole, ReadContract
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime
from ..tool_execution import run_required_tool_then_structure, validate_evidence_citations
from .models import D4Analysis, D4InvestigateOutput
from .prompt import SYSTEM_PROMPT
from .tools import build_tools


async def build_d4(invocation: AgentInvocation, runtime: AgentRuntime) -> D4InvestigateOutput:
    if invocation.task is None:
        raise ValueError("D4 requires a scoped task")
    tools = build_tools(invocation, runtime)
    analysis, evidence = await run_required_tool_then_structure(
        runtime=runtime,
        invocation=invocation,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Complaint: {invocation.case.complaint}\nTask: {invocation.task.question}\nWhy: {invocation.task.reason}",
        tools=tools,
        output_model=D4Analysis,
        role=AgentRole.D4,
        operation="investigate",
        max_tool_calls=4,
    )
    validate_evidence_citations(analysis.evidence_ids, evidence)
    read_contract = None
    if analysis.data_read_contract is not None:
        validate_evidence_citations(analysis.data_read_contract.code_evidence_ids, evidence)
        supporting_content = "\n".join(
            item.content
            for item in evidence
            if item.evidence_id in analysis.data_read_contract.code_evidence_ids
        )
        relation_marker = analysis.data_read_contract.relation
        if relation_marker not in supporting_content:
            raise ValueError(
                "D4 ReadContract relation is not named by its cited code/deployment evidence"
            )
        read_contract = ReadContract(
            contract_id=f"rc_{uuid.uuid4().hex}",
            **analysis.data_read_contract.model_dump(),
        )
    return D4InvestigateOutput(
        finding=AgentFinding(
            finding_id=f"finding_{uuid.uuid4().hex}",
            role=AgentRole.D4,
            answer=analysis.answer,
            observations=analysis.observations,
            evidence_ids=analysis.evidence_ids,
            limitations=analysis.limitations,
            read_contract=read_contract,
        )
    )
