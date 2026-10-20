from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...models import AgentFinding, ReadContract, SpecialistTask
from ..contracts import AgentInvocation


class D5InvestigateInput(AgentInvocation):
    operation: Literal["investigate"]
    task: SpecialistTask
    read_contract: ReadContract


class D5Analysis(BaseModel):
    answer: str = Field(min_length=1, max_length=1_600)
    observations: list[str] = Field(default_factory=list, max_length=10)
    evidence_ids: list[str] = Field(default_factory=list, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=6)


class D5InvestigateOutput(BaseModel):
    finding: AgentFinding
