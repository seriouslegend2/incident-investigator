from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from ...models import SPECIALIST_ROLES, AgentRole
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime
from .models import D1PlanOutput
from .prompt import SYSTEM_PROMPT
from .tools import build_tools


def _findings_text(invocation: AgentInvocation) -> str:
    if not invocation.findings:
        return "No evidence has been collected yet."
    blocks = []
    for finding in invocation.findings[-12:]:
        blocks.append(
            f"[{finding.role.value}] answer={finding.answer}; "
            f"evidence={','.join(finding.evidence_ids) or 'none'}; "
            f"limits={'; '.join(finding.limitations) or 'none'}"
        )
    return "\n".join(blocks)


async def build_d1(invocation: AgentInvocation, runtime: AgentRuntime) -> D1PlanOutput:
    available_roles = sorted(
        role.value
        for role in SPECIALIST_ROLES
        if role != AgentRole.D5 or invocation.read_contract is not None
    )
    requested_followups = (
        "\n".join(
            f"- {task.role.value}: {task.question} (reason: {task.reason})"
            for task in invocation.requested_follow_up_tasks
        )
        or "None."
    )
    prompt = f"""Case ID: {invocation.case.case_id}
Round: {invocation.round_index}
Complaint: {invocation.case.complaint}
Trusted scenario scope: {invocation.case.scope.scenario_id}
Available roles for this round: {", ".join(available_roles)}
D4 ReadContract available: {"yes" if invocation.read_contract else "no"}
D7 requested follow-ups (must be retained as tasks unless unsafe/blocked):
{requested_followups}
Prior findings:\n{_findings_text(invocation)}

Return the next plan now."""
    tools = build_tools(invocation, runtime)
    tools_by_name = {tool.name: tool for tool in tools}
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(prompt)]
    trace_config = runtime.trace_config(invocation, AgentRole.D1, "plan")
    response = (
        await runtime.model()
        .bind_tools(tools, tool_choice="required")
        .ainvoke(
            messages,
            config=trace_config,
        )
    )
    tool_messages: list[ToolMessage] = []
    fallback_scope = ""
    include_tool_response = bool(response.tool_calls) and len(response.tool_calls) <= 2
    if not include_tool_response:
        # Some model/provider combinations can return a structured text turn despite a required
        # tool choice, or exceed the planner's two-call budget. Never let D1 plan without a
        # routing packet in either case.
        fallback_scope = await tools_by_name["resolve_feature_scope"].ainvoke(
            {"query": invocation.case.complaint},
            config=trace_config,
        )
    else:
        for call in response.tool_calls:
            tool = tools_by_name.get(call["name"])
            if tool is None:
                raise ValueError(f"D1 requested disallowed topology tool {call['name']!r}")
            result = await tool.ainvoke(call["args"], config=trace_config)
            tool_messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    model = runtime.model().with_structured_output(D1PlanOutput, method="json_schema")
    output = await model.ainvoke(
        [
            *messages,
            *([response] if include_tool_response else []),
            *tool_messages,
            *(
                [
                    HumanMessage(
                        content=(
                            "Backend-provided candidate scope packet because the topology tool was "
                            f"not invoked: {fallback_scope}"
                        )
                    )
                ]
                if fallback_scope
                else []
            ),
        ],
        config=trace_config,
    )
    if (
        invocation.round_index >= runtime.settings.max_agent_rounds
        and output.next_action == "dispatch"
        and not invocation.requested_follow_up_tasks
    ):
        output = D1PlanOutput(
            next_action="send_to_critic",
            rationale=(
                "The configured investigation-round budget is exhausted; send the collected "
                "evidence to D7 for an independent approve/follow-up/withhold decision."
            ),
            tasks=[],
        )
    if output.next_action == "send_to_critic" and output.tasks:
        raise ValueError("D1 returned tasks while asking to send the case to D7")
    if output.next_action == "dispatch" and not output.tasks:
        raise ValueError("D1 selected dispatch without a specialist task")
    if invocation.requested_follow_up_tasks and output.next_action != "dispatch":
        raise ValueError("D1 cannot discard a D7 follow-up request")
    for task in output.tasks:
        if task.role not in SPECIALIST_ROLES:
            raise ValueError(f"D1 selected non-specialist role {task.role.value}")
        if task.role == AgentRole.D5 and invocation.read_contract is None:
            raise ValueError("D1 selected D5 without a D4 ReadContract")
    requested_roles = {task.role for task in invocation.requested_follow_up_tasks}
    returned_roles = {task.role for task in output.tasks}
    if not requested_roles.issubset(returned_roles):
        raise ValueError("D1 omitted a specialist role requested by D7")
    return output
