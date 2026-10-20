from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...models import ReportSection
from ..contracts import AgentInvocation


class D8WriteInput(AgentInvocation):
    operation: Literal["write"]


class D8DraftOutput(BaseModel):
    summary: str = Field(min_length=1, max_length=1_500)
    expected_flow: list[str] = Field(min_length=1, max_length=10)
    observed_flow: list[str] = Field(min_length=1, max_length=10)
    conclusion: str = Field(min_length=1, max_length=1_800)
    limitations: list[str] = Field(default_factory=list, max_length=8)
    recommended_next_steps: list[str] = Field(default_factory=list, max_length=8)
    sections: list[ReportSection] = Field(min_length=3, max_length=6)
    evidence_ids: list[str] = Field(default_factory=list, max_length=30)
