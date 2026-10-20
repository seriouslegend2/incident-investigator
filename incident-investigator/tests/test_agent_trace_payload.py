from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

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


@pytest.mark.asyncio
async def test_runtime_pulls_the_tagged_langsmith_prompt_then_caches_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    def pull(api_key: str, reference: str) -> str:
        calls.append((api_key, reference))
        return "managed prompt from LangSmith"

    monkeypatch.setattr(
        AgentRuntime,
        "_pull_langsmith_system_message",
        staticmethod(pull),
    )
    runtime = AgentRuntime(
        settings=SimpleNamespace(
            openai_model="test-model",
            langsmith_api_key=SimpleNamespace(get_secret_value=lambda: "test-key"),
        ),
        repository=None,
        gateway=None,
    )

    first = await runtime.resolve_prompt(AgentRole.D3, "investigate")
    second = await runtime.resolve_prompt(AgentRole.D3, "investigate")

    assert first.source == "langsmith"
    assert first.reference == "incident-investigator-d3-observability:v2"
    assert first.system_message == "managed prompt from LangSmith"
    assert second == first
    assert calls == [("test-key", "incident-investigator-d3-observability:v2")]
