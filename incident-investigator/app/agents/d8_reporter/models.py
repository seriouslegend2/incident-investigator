from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...models import RankedHypothesis, ReportSection
from ..contracts import AgentInvocation


class D8WriteInput(AgentInvocation):
    operation: Literal["write"]


class D8CitedSection(ReportSection):
    """D8's factual prose must point at at least one retrieved source record."""

    evidence_ids: list[str] = Field(default_factory=list, max_length=20)


class D8DraftOutput(BaseModel):
    summary: str = Field(min_length=1, max_length=1_500)
    expected_flow: list[str] = Field(min_length=1, max_length=10)
    observed_flow: list[str] = Field(min_length=1, max_length=10)
    conclusion: str = Field(min_length=1, max_length=1_800)
    ranked_hypotheses: list[RankedHypothesis] = Field(min_length=1, max_length=5)
    limitations: list[str] = Field(default_factory=list, max_length=8)
    recommended_next_steps: list[str] = Field(default_factory=list, max_length=8)
    sections: list[D8CitedSection] = Field(min_length=3, max_length=6)
    evidence_ids: list[str] = Field(default_factory=list, max_length=30)
