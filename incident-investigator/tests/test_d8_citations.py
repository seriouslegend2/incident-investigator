from __future__ import annotations

from app.agents.d8_reporter.executor import _draft_issues
from app.agents.d8_reporter.models import D8DraftOutput


def test_d8_delivery_check_detects_a_literal_none_id() -> None:
    output = D8DraftOutput.model_validate(
        {
            "summary": "Summary based on cited evidence.",
            "expected_flow": ["Expected event."],
            "observed_flow": ["Observed event."],
            "conclusion": "A bounded conclusion.",
            "ranked_hypotheses": [
                {
                    "rank": 1,
                    "statement": "The observed failure explains the complaint.",
                    "assessment": "supported",
                    "confidence": "medium",
                    "supporting_evidence_ids": ["ev_1"],
                    "contradicting_evidence_ids": [],
                    "missing_evidence": [],
                }
            ],
            "limitations": [],
            "recommended_next_steps": [],
            "sections": [
                {"title": "Expected", "text": "Expected event.", "evidence_ids": ["ev_1"]},
                {"title": "Observed", "text": "Observed event.", "evidence_ids": ["ev_1"]},
                {"title": "Invalid", "text": "No evidence.", "evidence_ids": ["none"]},
            ],
            "evidence_ids": ["ev_1"],
        }
    )
    assert _draft_issues(output, ["ev_1"]) == ["invalid evidence IDs: none"]
