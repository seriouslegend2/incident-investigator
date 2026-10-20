from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from langchain_openai import ChatOpenAI

from ..config import Settings
from ..db.repository import IncidentRepository
from ..models import AgentRole
from ..prompts import prompt_metadata
from ..tools.gateway import ToolGateway
from .contracts import AgentDefinition, AgentInvocation


@dataclass
class AgentRuntime:
    settings: Settings
    repository: IncidentRepository
    gateway: ToolGateway
    _case_trace_urls: dict[str, str] = field(default_factory=dict)

    def model(self) -> ChatOpenAI:
        self.settings.require_agent_runtime()
        return ChatOpenAI(
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key.get_secret_value(),
            temperature=0,
            max_retries=2,
        )

    def trace_config(
        self, invocation: AgentInvocation, role: AgentRole, operation: str
    ) -> dict[str, Any]:
        config: dict[str, Any] = {
            "run_name": f"incident/{role.value.lower()}/{operation}",
            "tags": ["incident-investigator", role.value.lower(), operation],
            "metadata": {
                "case_id": invocation.case.case_id,
                "task_id": invocation.task_id,
                "agent_run_id": invocation.run_id,
                "scenario_id": invocation.case.scope.scenario_id,
                **prompt_metadata(role, operation),
            },
        }
        return config

    def set_case_trace_url(self, case_id: str, trace_url: str) -> None:
        self._case_trace_urls[case_id] = trace_url

    def get_case_trace_url(self, case_id: str) -> str | None:
        return self._case_trace_urls.get(case_id)


async def invoke_definition(
    definition: AgentDefinition,
    invocation: AgentInvocation,
    runtime: AgentRuntime,
) -> Any:
    """Persist a started/finished agent run around the real model invocation."""

    if invocation.operation not in definition.operations:
        raise ValueError(f"{definition.name.value} does not implement {invocation.operation!r}")
    input_model, output_model = definition.operations[invocation.operation]
    input_model.model_validate(invocation.model_dump(mode="json"))
    await runtime.repository.begin_agent_run(
        run_id=invocation.run_id,
        case_id=invocation.case.case_id,
        task_id=invocation.task_id,
        role=definition.name,
        operation=invocation.operation,
        model_name=runtime.settings.openai_model,
        input_json={
            **invocation.model_dump(mode="json"),
            "prompt": prompt_metadata(definition.name, invocation.operation),
        },
    )
    try:
        result = await definition.build(invocation, runtime)
        validated = output_model.model_validate(result)
        await runtime.repository.finish_agent_run(
            invocation.run_id,
            output_json=validated.model_dump(mode="json"),
        )
        return validated
    except Exception as exc:
        await runtime.repository.finish_agent_run(invocation.run_id, error_message=str(exc)[:1_000])
        raise


def new_run_id() -> str:
    return f"arun_{uuid.uuid4().hex}"
