from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from app.agents.d1_orchestrator.definition import agent_definition
from app.agents.d1_orchestrator.models import D1PlanInput
from app.agents.runtime import AgentRuntime
from app.models import AgentRole, CaseScope, CaseStatus, IncidentCase
from app.prompts import prompt_spec


def test_agent_trace_exposes_the_prompt_scope_tools_and_handoff() -> None:
    runtime = AgentRuntime(
        settings=SimpleNamespace(openai_model="test-model"),
        repository=None,
        gateway=None,
    )
    invocation = D1PlanInput(
        case=IncidentCase(
            case_id="case_trace_test",
            complaint="A customer did not receive their confirmation message.",
            scope=CaseScope(scenario_id="email-confirmation-timeout"),
            requested_by="test",
            status=CaseStatus.OPEN,
            created_at=datetime.now(UTC),
        ),
        task_id="task_trace_test",
        run_id="arun_trace_test",
        operation="plan",
        round_index=0,
    )

    inputs = runtime.agent_trace_inputs(agent_definition, invocation)

    assert inputs["agent"]["role"] == AgentRole.D1.value
    assert inputs["agent"]["allowed_tools"] == [
        "resolve_feature_scope",
        "expand_dependency_path",
    ]
    assert inputs["prompt"]["system_message"] == prompt_spec(AgentRole.D1, "plan").system_prompt
    assert inputs["scoped_input"]["case"]["case_id"] == "case_trace_test"
    assert runtime.trace_config(invocation, AgentRole.D1, "plan")["run_name"] == "model/d1/plan"
