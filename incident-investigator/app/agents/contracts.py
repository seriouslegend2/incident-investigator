from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ..models import AgentFinding, AgentRole, IncidentCase, ReadContract, SpecialistTask


class AgentInvocation(BaseModel):
    """Small, durable task envelope modelled after KookarCore EDA2 invocations."""

    case: IncidentCase
    task_id: str
    run_id: str
    operation: str
    round_index: int
    task: SpecialistTask | None = None
    findings: list[AgentFinding] = []
    read_contract: ReadContract | None = None
    requested_follow_up_tasks: list[SpecialistTask] = []


if TYPE_CHECKING:
    from .runtime import AgentRuntime


AgentExecutor = Callable[[AgentInvocation, "AgentRuntime"], Awaitable[Any]]


@dataclass(frozen=True)
class AgentDefinition:
    """The exported object every folder must provide as ``agent_definition``."""

    name: AgentRole
    description: str
    default_model: str
    prompt_version: str
    allowed_tools: tuple[str, ...]
    operations: Mapping[str, tuple[type[BaseModel], type[BaseModel]]]
    build: AgentExecutor
