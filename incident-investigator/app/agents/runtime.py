from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from langchain_openai import ChatOpenAI
from langsmith.run_helpers import trace
from pydantic import BaseModel

from ..config import Settings
from ..db.repository import IncidentRepository
from ..models import AgentRole
from ..prompts import prompt_metadata, prompt_spec
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
        """Configuration for the provider calls inside one named agent span.

        The explicit agent span is created by ``agent_trace`` below.  These
        names deliberately identify the *model step* rather than pretending a
        provider call is the whole agent.  That leaves a readable hierarchy in
        LangSmith: workflow -> agent -> model/tool calls.
        """

        config: dict[str, Any] = {
            "run_name": f"model/{role.value.lower()}/{operation}",
            "tags": ["incident-investigator", "model", role.value.lower(), operation],
            "metadata": {
                "case_id": invocation.case.case_id,
                "task_id": invocation.task_id,
                "agent_run_id": invocation.run_id,
                "scenario_id": invocation.case.scope.scenario_id,
                **prompt_metadata(role, operation),
            },
        }
        return config

    def agent_trace_inputs(
        self, definition: AgentDefinition, invocation: AgentInvocation
    ) -> dict[str, Any]:
        """Return the auditable, non-secret envelope shown on an agent span.

        A LangSmith user should be able to open *one agent run* and answer:
        which role ran, which exact prompt governed it, what scoped task it
        received, and which tools it was allowed to invoke.  Credentials and
        connector configuration never belong in this envelope.
        """

        spec = prompt_spec(definition.name, invocation.operation)
        return {
            "agent": {
                "role": definition.name.value,
                "operation": invocation.operation,
                "description": definition.description,
                "model": self.settings.openai_model,
                "allowed_tools": list(definition.allowed_tools),
            },
            "prompt": {
                **prompt_metadata(definition.name, invocation.operation),
                "system_message": spec.system_prompt,
            },
            "scoped_input": invocation.model_dump(mode="json"),
        }

    def agent_trace_output(self, result: BaseModel) -> dict[str, Any]:
        """Persist the structured response and a human-readable handoff."""

        output = result.model_dump(mode="json")
        handoff: dict[str, Any] = {"next": "return structured output to LangGraph"}
        if "tasks" in output:
            handoff = {
                "next": output.get("next_action", "send_to_critic"),
                "delegations": output.get("tasks", []),
            }
        elif "finding" in output:
            finding = output["finding"]
            handoff = {
                "next": "join other selected specialist findings, then D7 reviews them",
                "evidence_ids": finding.get("evidence_ids", []),
            }
        elif "decision" in output:
            handoff = {
                "next": output["decision"],
                "follow_up_tasks": output.get("follow_up_tasks", []),
            }
        elif "summary" in output:
            handoff = {"next": "D7 reviews this exact D8 draft before delivery"}
        return {"structured_output": output, "handoff": handoff}

    @asynccontextmanager
    async def agent_trace(
        self, definition: AgentDefinition, invocation: AgentInvocation
    ) -> AsyncIterator[Any | None]:
        """Create one explicit LangSmith span for one agent invocation.

        This mirrors KookarCore's request-scoped agent boundary. ``parent`` is
        intentionally ignored: each invoked D-agent is a separate *root trace*
        in the LangSmith project (not merely a node hidden inside LangGraph's
        workflow trace). Case/task/agent-run metadata keeps those root traces
        correlatable, while model and source-tool spans remain nested below
        the individual agent that called them.
        """

        if not self.settings.langsmith_tracing:
            yield None
            return
        async with trace(
            name=f"agent/{definition.name.value.lower()}/{invocation.operation}",
            run_type="chain",
            inputs=self.agent_trace_inputs(definition, invocation),
            project_name=self.settings.langsmith_project,
            parent="ignore",
            tags=[
                "incident-investigator",
                "multi-agent",
                "agent",
                definition.name.value.lower(),
                invocation.operation,
            ],
            metadata={
                "case_id": invocation.case.case_id,
                "task_id": invocation.task_id,
                "agent_run_id": invocation.run_id,
                "scenario_id": invocation.case.scope.scenario_id,
                **prompt_metadata(definition.name, invocation.operation),
            },
        ) as run:
            yield run

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
        async with runtime.agent_trace(definition, invocation) as agent_run:
            result = await definition.build(invocation, runtime)
            validated = output_model.model_validate(result)
            await runtime.repository.finish_agent_run(
                invocation.run_id,
                output_json=validated.model_dump(mode="json"),
            )
            if agent_run is not None:
                agent_run.end(outputs=runtime.agent_trace_output(validated))
            return validated
    except Exception as exc:
        await runtime.repository.finish_agent_run(invocation.run_id, error_message=str(exc)[:1_000])
        raise


def new_run_id() -> str:
    return f"arun_{uuid.uuid4().hex}"
