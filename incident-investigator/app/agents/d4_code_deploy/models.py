from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...models import AgentFinding, SpecialistTask
from ..contracts import AgentInvocation


class D4InvestigateInput(AgentInvocation):
    operation: Literal["investigate"]
    task: SpecialistTask


class ReadContractProposal(BaseModel):
    relation: Literal[
        "delivery_events", "customer_preferences", "payment_attempts", "inventory_events"
    ]
    lookup_field: Literal["message_id", "customer_id", "payment_id", "sku"]
    lookup_value: str = Field(min_length=1, max_length=200)
    code_evidence_ids: list[str] = Field(min_length=1, max_length=8)
    reason: str = Field(min_length=12, max_length=500)


class D4Analysis(BaseModel):
    answer: str = Field(min_length=1, max_length=1_600)
    observations: list[str] = Field(default_factory=list, max_length=10)
    evidence_ids: list[str] = Field(default_factory=list, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=6)
    data_read_contract: ReadContractProposal | None = None


class D4InvestigateOutput(BaseModel):
    finding: AgentFinding
