from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from ...models import AgentRole
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime
from .models import D8DraftOutput
from .prompt import SYSTEM_PROMPT


async def build_d8(invocation: AgentInvocation, runtime: AgentRuntime) -> D8DraftOutput:
    available_ids = [
        evidence_id for item in invocation.findings for evidence_id in item.evidence_ids
    ]
    findings = "\n".join(
        f"[{item.role.value}] {item.answer}\nObservations: {'; '.join(item.observations)}\n"
        f"Evidence: {', '.join(item.evidence_ids) or 'none'}\nLimits: {'; '.join(item.limitations) or 'none'}"
        for item in invocation.findings
    )
    prompt = f"""Case ID: {invocation.case.case_id}
Original complaint: {invocation.case.complaint}
Available evidence IDs: {", ".join(available_ids) or "none"}
Reviewed findings:\n{findings}

Draft the report now."""
    model = runtime.model().with_structured_output(D8DraftOutput, method="json_schema")
    output = await model.ainvoke(
        [SystemMessage(SYSTEM_PROMPT), HumanMessage(prompt)],
        config=runtime.trace_config(invocation, AgentRole.D8, "write"),
    )
    unknown = set(output.evidence_ids) - set(available_ids)
    if unknown:
        raise ValueError("D8 cited unprovided evidence: " + ", ".join(sorted(unknown)))
    for section in output.sections:
        unknown_section = set(section.evidence_ids) - set(available_ids)
        if unknown_section:
            raise ValueError(
                "D8 section cited unprovided evidence: " + ", ".join(sorted(unknown_section))
            )
    return output
