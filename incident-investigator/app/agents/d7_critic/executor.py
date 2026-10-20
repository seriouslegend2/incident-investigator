from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from ...models import SPECIALIST_ROLES, AgentRole
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime
from .models import D7ReportReviewInput, D7ReportReviewOutput, D7ReviewOutput
from .prompt import REPORT_REVIEW_PROMPT, SYSTEM_PROMPT


async def _evidence_text(invocation: AgentInvocation, runtime: AgentRuntime) -> str:
    evidence_ids = [
        evidence_id for finding in invocation.findings for evidence_id in finding.evidence_ids
    ]
    records = await runtime.repository.get_case_evidence(
        case_id=invocation.case.case_id,
        evidence_ids=evidence_ids,
    )
    if not records:
        return "No cited source records were available to independently inspect."
    return "\n\n".join(
        f"[{record['evidence_id']}] source={record['source_kind']} "
        f"summary={record['summary']}\ncontent={record['content']}\n"
        f"coverage={record['coverage_note']}"
        for record in records
    )


async def build_d7(
    invocation: AgentInvocation,
    runtime: AgentRuntime,
) -> D7ReviewOutput | D7ReportReviewOutput:
    if invocation.operation == "review_report":
        report_invocation = D7ReportReviewInput.model_validate(invocation)
        return await build_d7_report_review(report_invocation, runtime)
    if invocation.operation != "review":
        raise ValueError(f"Unsupported D7 operation: {invocation.operation}")
    findings = (
        "\n".join(
            f"[{item.role.value}] {item.answer}\nEvidence: {', '.join(item.evidence_ids) or 'none'}\n"
            f"Limits: {'; '.join(item.limitations) or 'none'}"
            for item in invocation.findings
        )
        or "No findings returned."
    )
    source_evidence = await _evidence_text(invocation, runtime)
    prompt = f"""Case ID: {invocation.case.case_id}
Complaint: {invocation.case.complaint}
D4 ReadContract available: {"yes" if invocation.read_contract else "no"}
Findings to challenge:\n{findings}

Original records behind cited IDs:\n{source_evidence}

Return an independent review decision."""
    model = runtime.model().with_structured_output(D7ReviewOutput, method="json_schema")
    correction = ""
    for attempt in range(2):
        output = await model.ainvoke(
            [SystemMessage(SYSTEM_PROMPT), HumanMessage(prompt + correction)],
            config=runtime.trace_config(invocation, AgentRole.D7, "review"),
        )
        issues = _review_issues(output, has_read_contract=invocation.read_contract is not None)
        if not issues:
            return output
        if attempt == 0:
            correction = (
                "\n\nYour previous review violated this output rule: "
                + "; ".join(issues)
                + ". Return a corrected structured review."
            )
            continue
        return D7ReviewOutput(
            decision="withhold",
            rationale="Critic output was malformed after one correction attempt; the case is withheld.",
            follow_up_tasks=[],
            unsupported_claims=issues,
        )
    raise AssertionError("unreachable D7 review-correction loop")


def _review_issues(output: D7ReviewOutput, *, has_read_contract: bool) -> list[str]:
    issues: list[str] = []
    for task in output.follow_up_tasks:
        if task.role not in SPECIALIST_ROLES:
            issues.append(f"D7 selected non-specialist role {task.role.value}")
        if task.role == AgentRole.D5 and not has_read_contract:
            issues.append("D7 selected D5 without a D4 ReadContract")
    if output.decision != "request_follow_up" and output.follow_up_tasks:
        issues.append("only request_follow_up may include follow-up tasks")
    if output.decision == "request_follow_up" and not output.follow_up_tasks:
        issues.append("request_follow_up requires at least one task")
    return issues


async def build_d7_report_review(
    invocation: D7ReportReviewInput,
    runtime: AgentRuntime,
) -> D7ReportReviewOutput:
    finding_text = (
        "\n".join(
            f"[{item.role.value}] {item.answer}\nEvidence: {', '.join(item.evidence_ids) or 'none'}"
            for item in invocation.findings
        )
        or "No reviewed findings."
    )
    source_evidence = await _evidence_text(invocation, runtime)
    prompt = f"""Case ID: {invocation.case.case_id}
Reviewed findings:\n{finding_text}

Original records behind cited IDs:\n{source_evidence}

Exact D8 draft JSON:\n{invocation.draft}

Return the final delivery decision."""
    model = runtime.model().with_structured_output(D7ReportReviewOutput, method="json_schema")
    return await model.ainvoke(
        [SystemMessage(REPORT_REVIEW_PROMPT), HumanMessage(prompt)],
        config=runtime.trace_config(invocation, AgentRole.D7, "review_report"),
    )
