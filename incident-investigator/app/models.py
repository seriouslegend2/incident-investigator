from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    D1 = "D1"
    D3 = "D3"
    D4 = "D4"
    D5 = "D5"
    D6 = "D6"
    D7 = "D7"
    D8 = "D8"


SPECIALIST_ROLES = frozenset({AgentRole.D3, AgentRole.D4, AgentRole.D5, AgentRole.D6})


class CaseStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    REVIEWING = "reviewing"
    DELIVERED = "delivered"
    WITHHELD = "withheld"
    FAILED = "failed"


class CaseScope(BaseModel):
    """Trusted scope is created by the API, not selected by the model/tool arguments."""

    environment: Literal["demo"] = "demo"
    scenario_id: str
    tenant_id: str = "demo-tenant-a"


class CreateInvestigationRequest(BaseModel):
    complaint: str = Field(min_length=8, max_length=2_000)
    scenario_id: str = Field(
        description="Seeded demo-source partition. In production this is derived from authenticated scope."
    )
    requested_by: str = Field(default="demo-operator", min_length=2, max_length=120)


class IncidentCase(BaseModel):
    case_id: str
    complaint: str
    scope: CaseScope
    requested_by: str
    status: CaseStatus
    created_at: datetime


class SpecialistTask(BaseModel):
    role: AgentRole
    question: str = Field(min_length=12, max_length=700)
    reason: str = Field(min_length=8, max_length=400)


class EvidenceRecord(BaseModel):
    evidence_id: str
    source_kind: Literal["observability", "code_deploy", "data", "ai_runtime"]
    source_record_id: str
    observed_at: datetime
    summary: str
    coverage_note: str
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)


class ReadContract(BaseModel):
    """D4-proposed, backend-validated path that permits one bounded D5 query."""

    contract_id: str
    relation: Literal[
        "delivery_events", "customer_preferences", "payment_attempts", "inventory_events"
    ]
    lookup_field: Literal["message_id", "customer_id", "payment_id", "sku"]
    lookup_value: str = Field(min_length=1, max_length=200)
    code_evidence_ids: list[str] = Field(min_length=1, max_length=8)
    reason: str = Field(min_length=12, max_length=500)


class AgentFinding(BaseModel):
    finding_id: str
    role: AgentRole
    answer: str = Field(min_length=1, max_length=2_000)
    observations: list[str] = Field(default_factory=list, max_length=12)
    evidence_ids: list[str] = Field(default_factory=list, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=8)
    read_contract: ReadContract | None = None


class CriticDecision(BaseModel):
    decision: Literal["approve", "request_follow_up", "withhold"]
    rationale: str = Field(min_length=1, max_length=1_500)
    follow_up_tasks: list[SpecialistTask] = Field(default_factory=list, max_length=2)
    unsupported_claims: list[str] = Field(default_factory=list, max_length=8)


class ReportSection(BaseModel):
    title: str
    text: str
    evidence_ids: list[str] = Field(default_factory=list)


class IncidentReport(BaseModel):
    case_id: str
    status: Literal["delivered", "withheld"]
    summary: str
    expected_flow: list[str]
    observed_flow: list[str]
    conclusion: str
    limitations: list[str]
    recommended_next_steps: list[str]
    sections: list[ReportSection]
    evidence_ids: list[str]
    reviewed_by_d7: bool
    created_at: datetime


class InvestigationResponse(BaseModel):
    case: IncidentCase
    report: IncidentReport | None = None


class SourceCatalogEntry(BaseModel):
    source_kind: Literal["observability", "code_deploy", "data", "ai_runtime"]
    description: str
    tool_name: str
    requires_read_contract: bool = False
