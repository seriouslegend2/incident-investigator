from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from ...models import CriticDecision
from ..contracts import AgentInvocation


class D7ReviewInput(AgentInvocation):
    operation: Literal["review"]


class D7ReviewOutput(CriticDecision):
    pass


class D7ReportReviewInput(AgentInvocation):
    operation: Literal["review_report"]
    draft: dict[str, Any]


class D7ReportReviewOutput(BaseModel):
    decision: Literal["approve", "withhold"]
    rationale: str
    unsupported_claims: list[str] = Field(default_factory=list, max_length=8)
