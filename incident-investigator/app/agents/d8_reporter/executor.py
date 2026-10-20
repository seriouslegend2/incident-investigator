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
    correction = ""
    for attempt in range(2):
        output = await model.ainvoke(
            [SystemMessage(SYSTEM_PROMPT), HumanMessage(prompt + correction)],
            config=runtime.trace_config(invocation, AgentRole.D8, "write"),
        )
        issues = _draft_issues(output, available_ids)
        if not issues:
            return output
        if attempt == 1:
            raise ValueError("D8 draft failed delivery checks: " + "; ".join(issues))
        correction = (
            "\n\nYour previous draft failed these delivery checks: "
            + "; ".join(issues)
            + ". Return a corrected report using only these IDs: "
            + (", ".join(available_ids) or "none")
            + ". Do not use the word 'none' as an evidence ID. Every section needs a real evidence ID."
        )
    raise AssertionError("unreachable D8 citation-correction loop")


def _draft_issues(output: D8DraftOutput, available_ids: list[str]) -> list[str]:
    cited = set(output.evidence_ids)
    for section in output.sections:
        cited.update(section.evidence_ids)
    for hypothesis in output.ranked_hypotheses:
        cited.update(hypothesis.supporting_evidence_ids)
        cited.update(hypothesis.contradicting_evidence_ids)
    issues = (
        ["invalid evidence IDs: " + ", ".join(sorted(cited - set(available_ids)))]
        if cited - set(available_ids)
        else []
    )
    if [item.rank for item in output.ranked_hypotheses] != list(
        range(1, len(output.ranked_hypotheses) + 1)
    ):
        issues.append("hypothesis ranks must be consecutive from 1")
    if any(not section.evidence_ids for section in output.sections):
        issues.append("every report section needs at least one evidence ID")
    for hypothesis in output.ranked_hypotheses:
        if (
            hypothesis.assessment in {"supported", "possible"}
            and not hypothesis.supporting_evidence_ids
        ):
            issues.append(f"hypothesis #{hypothesis.rank} needs supporting evidence")
        if hypothesis.assessment == "insufficient" and hypothesis.confidence != "low":
            issues.append(
                f"hypothesis #{hypothesis.rank} must use low confidence when insufficient"
            )
    return issues
