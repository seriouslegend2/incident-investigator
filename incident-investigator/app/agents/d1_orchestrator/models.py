from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ...models import SpecialistTask
from ..contracts import AgentInvocation


class D1PlanInput(AgentInvocation):
    operation: Literal["plan"]


class D1PlanOutput(BaseModel):
    next_action: Literal["dispatch", "send_to_critic"]
    rationale: str = Field(min_length=1, max_length=1_500)
    tasks: list[SpecialistTask] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def one_task_per_specialist_in_a_parallel_batch(self) -> "D1PlanOutput":
        """Keep one D1 batch independently executable and safely joinable."""

        roles = [task.role for task in self.tasks]
        if len(roles) != len(set(roles)):
            raise ValueError("A parallel D1 batch may contain at most one task per specialist")
        return self
