from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from langchain_core.tracers.context import tracing_v2_enabled
from langgraph.graph import END, START, StateGraph
from langsmith import Client

from ..agents.registry import get_agent
from ..agents.runtime import AgentRuntime, invoke_definition, new_run_id
from ..models import (
    AgentFinding,
    AgentRole,
    CaseStatus,
    IncidentCase,
    IncidentReport,
    ReportSection,
)
from .state import InvestigationState


def _latest_read_contract(findings: list[AgentFinding]) -> Any:
    for finding in reversed(findings):
        if finding.read_contract is not None:
            return finding.read_contract
    return None


async def run_d1_plan(state: InvestigationState, runtime: AgentRuntime) -> dict[str, Any]:
    case = state["case"]
    findings = state.get("findings", [])
    contract = state.get("read_contract") or _latest_read_contract(findings)
    invocation = {
        "case": case,
        "task_id": f"task_{uuid.uuid4().hex}",
        "run_id": new_run_id(),
        "operation": "plan",
        "round_index": state.get("round_index", 0),
        "findings": findings,
        "read_contract": contract,
        "requested_follow_up_tasks": state.get("requested_follow_up_tasks", []),
    }
    plan = await invoke_definition(
        get_agent(AgentRole.D1),
        get_agent(AgentRole.D1).operations["plan"][0].model_validate(invocation),
        runtime,
    )
    return {
        "d1_plan": plan,
        "pending_tasks": plan.tasks,
        "round_index": state.get("round_index", 0) + 1,
        "next_action": "dispatch" if plan.next_action == "dispatch" else "critic",
        "requested_follow_up_tasks": [],
        **({"read_contract": contract} if contract is not None else {}),
    }


PARALLEL_SPECIALIST_NODES: dict[AgentRole, str] = {
    AgentRole.D3: "run_d3",
    AgentRole.D4: "run_d4",
    AgentRole.D5: "run_d5",
    AgentRole.D6: "run_d6",
}


def dispatch_from_d1(
    state: InvestigationState,
) -> list[Literal["run_d3", "run_d4", "run_d5", "run_d6"]] | Literal["d7_review"]:
    """Fan out one D1 batch, then let the graph's static edge form the join.

    We schedule all four role branches so the LangGraph multi-source edge can
    deterministically wait for every branch. A role with no selected task is a
    no-op: it makes no model or source-tool call. This prevents the former
    bug where each completed dynamic branch independently invoked D1 again.
    """

    if state["next_action"] != "dispatch" or not state.get("pending_tasks"):
        return "d7_review"
    return list(PARALLEL_SPECIALIST_NODES.values())


async def run_specialist_for_role(
    state: InvestigationState, runtime: AgentRuntime, role: AgentRole
) -> dict[str, Any]:
    """Run this role's one planned task, or return a no-op at the batch barrier."""

    if role not in PARALLEL_SPECIALIST_NODES:
        raise ValueError(f"{role.value} cannot be dispatched as an evidence specialist")
    tasks = [task for task in state.get("pending_tasks", []) if task.role == role]
    if not tasks:
        return {}
    if len(tasks) != 1:
        raise ValueError(f"D1 selected more than one {role.value} task in one parallel batch")
    task = tasks[0]
    invocation = {
        "case": state["case"],
        "task_id": f"task_{uuid.uuid4().hex}",
        "run_id": new_run_id(),
        "operation": "investigate",
        "round_index": state["round_index"],
        "task": task,
        "read_contract": state.get("read_contract"),
    }
    definition = get_agent(task.role)
    output = await invoke_definition(
        definition,
        definition.operations["investigate"][0].model_validate(invocation),
        runtime,
    )
    finding = output.finding
    await runtime.repository.save_finding(
        case_id=state["case"].case_id,
        task_id=invocation["task_id"],
        finding=finding,
    )
    update: dict[str, Any] = {"findings": [finding]}
    if finding.read_contract is not None:
        update["read_contract"] = finding.read_contract
    return update


async def run_d7_review(state: InvestigationState, runtime: AgentRuntime) -> dict[str, Any]:
    case = state["case"]
    invocation = {
        "case": case,
        "task_id": f"task_{uuid.uuid4().hex}",
        "run_id": new_run_id(),
        "operation": "review",
        "round_index": state.get("round_index", 0),
        "findings": state.get("findings", []),
        "read_contract": state.get("read_contract"),
    }
    definition = get_agent(AgentRole.D7)
    review = await invoke_definition(
        definition,
        definition.operations["review"][0].model_validate(invocation),
        runtime,
    )
    next_action = {"approve": "write", "withhold": "withhold", "request_follow_up": "replan"}[
        review.decision
    ]
    update: dict[str, Any] = {"d7_review": review, "next_action": next_action}
    if review.decision == "request_follow_up":
        update["requested_follow_up_tasks"] = review.follow_up_tasks
        update["critic_followup_count"] = state.get("critic_followup_count", 0) + 1
    return update


def after_d7_review(
    state: InvestigationState,
) -> Literal["d1_plan", "d8_write", "finalize_withheld"]:
    if state["next_action"] == "write":
        return "d8_write"
    if state["next_action"] == "withhold":
        return "finalize_withheld"
    if state.get("critic_followup_count", 0) > state.get("critic_followup_limit", 2):
        return "finalize_withheld"
    return "d1_plan"


async def run_d8_write(state: InvestigationState, runtime: AgentRuntime) -> dict[str, Any]:
    case = state["case"]
    invocation = {
        "case": case,
        "task_id": f"task_{uuid.uuid4().hex}",
        "run_id": new_run_id(),
        "operation": "write",
        "round_index": state.get("round_index", 0),
        "findings": state.get("findings", []),
        "read_contract": state.get("read_contract"),
    }
    definition = get_agent(AgentRole.D8)
    draft = await invoke_definition(
        definition,
        definition.operations["write"][0].model_validate(invocation),
        runtime,
    )
    return {"d8_draft": draft, "next_action": "deliver"}


async def run_d7_report_review(state: InvestigationState, runtime: AgentRuntime) -> dict[str, Any]:
    case = state["case"]
    definition = get_agent(AgentRole.D7)
    invocation = {
        "case": case,
        "task_id": f"task_{uuid.uuid4().hex}",
        "run_id": new_run_id(),
        "operation": "review_report",
        "round_index": state.get("round_index", 0),
        "findings": state.get("findings", []),
        "read_contract": state.get("read_contract"),
        "draft": state["d8_draft"].model_dump(mode="json"),
    }
    review = await invoke_definition(
        definition,
        definition.operations["review_report"][0].model_validate(invocation),
        runtime,
    )
    return {
        "d7_report_review": review,
        "next_action": "deliver" if review.decision == "approve" else "withhold",
    }


async def finalize_delivered(state: InvestigationState, runtime: AgentRuntime) -> dict[str, Any]:
    draft = state["d8_draft"]
    report = IncidentReport(
        case_id=state["case"].case_id,
        status="delivered",
        **draft.model_dump(),
        reviewed_by_d7=True,
        created_at=datetime.now(UTC),
    )
    await runtime.repository.save_report(f"report_{uuid.uuid4().hex}", report)
    await runtime.repository.update_case_status(report.case_id, CaseStatus.DELIVERED)
    return {"report": report}


async def finalize_withheld(state: InvestigationState, runtime: AgentRuntime) -> dict[str, Any]:
    review = state.get("d7_report_review") or state["d7_review"]
    evidence_ids = [
        evidence_id for finding in state.get("findings", []) for evidence_id in finding.evidence_ids
    ]
    report = IncidentReport(
        case_id=state["case"].case_id,
        status="withheld",
        summary="Incident report withheld pending independent evidence review.",
        expected_flow=[],
        observed_flow=[],
        conclusion="No incident conclusion was delivered.",
        limitations=[review.rationale, *review.unsupported_claims],
        recommended_next_steps=[task.question for task in getattr(review, "follow_up_tasks", [])],
        sections=[
            ReportSection(
                title="Independent review status",
                text=review.rationale,
                evidence_ids=evidence_ids,
            )
        ],
        evidence_ids=evidence_ids,
        reviewed_by_d7=False,
        created_at=datetime.now(UTC),
    )
    await runtime.repository.save_report(f"report_{uuid.uuid4().hex}", report)
    await runtime.repository.update_case_status(report.case_id, CaseStatus.WITHHELD)
    return {"report": report}


def build_graph(runtime: AgentRuntime) -> Any:
    async def d1_node(state: InvestigationState) -> dict[str, Any]:
        return await run_d1_plan(state, runtime)

    async def d3_node(state: InvestigationState) -> dict[str, Any]:
        return await run_specialist_for_role(state, runtime, AgentRole.D3)

    async def d4_node(state: InvestigationState) -> dict[str, Any]:
        return await run_specialist_for_role(state, runtime, AgentRole.D4)

    async def d5_node(state: InvestigationState) -> dict[str, Any]:
        return await run_specialist_for_role(state, runtime, AgentRole.D5)

    async def d6_node(state: InvestigationState) -> dict[str, Any]:
        return await run_specialist_for_role(state, runtime, AgentRole.D6)

    async def d7_node(state: InvestigationState) -> dict[str, Any]:
        return await run_d7_review(state, runtime)

    async def d8_node(state: InvestigationState) -> dict[str, Any]:
        return await run_d8_write(state, runtime)

    async def d7_report_node(state: InvestigationState) -> dict[str, Any]:
        return await run_d7_report_review(state, runtime)

    async def delivered_node(state: InvestigationState) -> dict[str, Any]:
        return await finalize_delivered(state, runtime)

    async def withheld_node(state: InvestigationState) -> dict[str, Any]:
        return await finalize_withheld(state, runtime)

    graph = StateGraph(InvestigationState)
    graph.add_node("d1_plan", d1_node)
    graph.add_node("run_d3", d3_node)
    graph.add_node("run_d4", d4_node)
    graph.add_node("run_d5", d5_node)
    graph.add_node("run_d6", d6_node)
    graph.add_node("d7_review", d7_node)
    graph.add_node("d8_write", d8_node)
    graph.add_node("d7_report_review", d7_report_node)
    graph.add_node("finalize_delivered", delivered_node)
    graph.add_node("finalize_withheld", withheld_node)
    graph.add_edge(START, "d1_plan")
    graph.add_conditional_edges(
        "d1_plan",
        dispatch_from_d1,
        ["run_d3", "run_d4", "run_d5", "run_d6", "d7_review"],
    )
    graph.add_edge(["run_d3", "run_d4", "run_d5", "run_d6"], "d7_review")
    graph.add_conditional_edges(
        "d7_review", after_d7_review, ["d1_plan", "d8_write", "finalize_withheld"]
    )
    graph.add_edge("d8_write", "d7_report_review")
    graph.add_conditional_edges(
        "d7_report_review",
        lambda state: (
            "finalize_delivered" if state["next_action"] == "deliver" else "finalize_withheld"
        ),
        ["finalize_delivered", "finalize_withheld"],
    )
    graph.add_edge("finalize_delivered", END)
    graph.add_edge("finalize_withheld", END)
    return graph.compile()


async def investigate(case: IncidentCase, runtime: AgentRuntime) -> IncidentReport:
    await runtime.repository.update_case_status(case.case_id, CaseStatus.INVESTIGATING)
    initial_state = {
        "case": case,
        "round_index": 0,
        "findings": [],
        "critic_followup_count": 0,
        "critic_followup_limit": runtime.settings.max_critic_followups,
        "requested_follow_up_tasks": [],
    }
    graph_config = {
        "recursion_limit": 40,
        "run_name": "incident/investigation",
        "tags": ["incident-investigator", "case-workflow"],
        "metadata": {
            "case_id": case.case_id,
            "scenario_id": case.scope.scenario_id,
        },
    }
    try:
        graph = build_graph(runtime)
        if runtime.settings.langsmith_tracing:
            client = Client(api_key=runtime.settings.langsmith_api_key.get_secret_value())
            with tracing_v2_enabled(
                project_name=runtime.settings.langsmith_project,
                client=client,
                tags=["incident-investigator", "case-workflow"],
            ) as tracer:
                result = await graph.ainvoke(initial_state, graph_config)
            client.flush()
            runtime.set_case_trace_url(case.case_id, tracer.get_run_url())
        else:
            result = await graph.ainvoke(initial_state, graph_config)
        return IncidentReport.model_validate(result["report"])
    except Exception:
        await runtime.repository.update_case_status(case.case_id, CaseStatus.FAILED)
        raise
