from __future__ import annotations

import pytest

from app.agents.tool_execution import ToolProtocolError, validate_evidence_citations
from app.models import EvidenceRecord


def test_evidence_citation_guard_rejects_fabricated_id() -> None:
    evidence = [
        EvidenceRecord.model_validate(
            {
                "evidence_id": "ev_real",
                "source_kind": "observability",
                "source_record_id": "source-1",
                "observed_at": "2026-10-20T09:15:00Z",
                "summary": "Observed event",
                "coverage_note": "Bounded demo source",
                "content": "request_id=req-1",
            }
        )
    ]
    with pytest.raises(ToolProtocolError, match="ev_invented"):
        validate_evidence_citations(["ev_real", "ev_invented"], evidence)
