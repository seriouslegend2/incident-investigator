from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...models import SpecialistTask
from ..contracts import AgentInvocation


class D1PlanInput(AgentInvocation):
    operation: Literal["plan"]


class D1PlanOutput(BaseModel):
    next_action: Literal["dispatch", "send_to_critic"]
    rationale: str = Field(min_length=1, max_length=1_500)
    tasks: list[SpecialistTask] = Field(default_factory=list, max_length=3)
