from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import IncidentReport


def _report_payload() -> dict[str, object]:
    return {
        "case_id": "case_demo",
        "status": "delivered",
        "summary": "A bounded evidence-grounded summary.",
        "expected_flow": ["Request enters the service."],
        "observed_flow": ["A downstream request failed."],
        "conclusion": "One explanation has the strongest available support.",
        "ranked_hypotheses": [
            {
                "rank": 1,
                "statement": "The downstream request failed before completion.",
                "assessment": "supported",
                "confidence": "medium",
                "supporting_evidence_ids": ["ev_1"],
                "contradicting_evidence_ids": [],
                "missing_evidence": [],
            }
        ],
        "limitations": [],
        "recommended_next_steps": [],
        "sections": [],
        "evidence_ids": ["ev_1"],
        "reviewed_by_d7": True,
        "created_at": "2026-10-20T09:15:00Z",
    }


def test_report_preserves_ranked_evidence_for_and_against() -> None:
    report = IncidentReport.model_validate(_report_payload())
    assert report.ranked_hypotheses[0].supporting_evidence_ids == ["ev_1"]
    assert report.ranked_hypotheses[0].contradicting_evidence_ids == []


def test_report_rejects_non_consecutive_hypothesis_ranks() -> None:
    payload = _report_payload()
    payload["ranked_hypotheses"] = [
        {
            "rank": 2,
            "statement": "Incorrectly ordered explanation.",
            "assessment": "possible",
            "confidence": "low",
            "supporting_evidence_ids": [],
            "contradicting_evidence_ids": [],
            "missing_evidence": ["More evidence is needed."],
        }
    ]
    with pytest.raises(ValidationError, match="ordered consecutively"):
        IncidentReport.model_validate(payload)
