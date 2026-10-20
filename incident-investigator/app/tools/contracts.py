from __future__ import annotations

from pydantic import BaseModel, Field

from ..models import EvidenceRecord


class EvidenceSearchInput(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=400,
        description="Focused keywords for records within this already-authorized investigation scope.",
    )


class EvidenceSearchOutput(BaseModel):
    evidence: list[EvidenceRecord]
    result_count: int
    coverage_note: str


class ScopeLookupOutput(BaseModel):
    candidate_services: list[str] = Field(default_factory=list, max_length=8)
    candidate_paths: list[str] = Field(default_factory=list, max_length=12)
    coverage_note: str
