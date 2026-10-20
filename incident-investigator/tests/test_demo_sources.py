from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.agents.d5_data.models import D5InvestigateInput
from app.db.demo_seed import DEMO_SCENARIOS
from app.models import AgentRole


def test_demo_source_catalog_has_at_least_ten_scenarios_and_no_stored_diagnosis() -> None:
    assert len(DEMO_SCENARIOS) >= 10
    assert len({item["scenario_id"] for item in DEMO_SCENARIOS}) == len(DEMO_SCENARIOS)
    forbidden_keys = {"outcome", "root_cause", "conclusion", "expected_answer", "diagnosis"}
    for scenario in DEMO_SCENARIOS:
        assert forbidden_keys.isdisjoint(scenario)
        assert scenario["records"]


def test_d5_input_contract_requires_a_read_contract() -> None:
    with pytest.raises(ValidationError):
        D5InvestigateInput.model_validate(
            {
                "case": {
                    "case_id": "case_test",
                    "complaint": "A customer says the message did not arrive.",
                    "scope": {"scenario_id": "message-reminder"},
                    "requested_by": "test",
                    "status": "open",
                    "created_at": "2026-10-20T00:00:00Z",
                },
                "task_id": "task_test",
                "run_id": "run_test",
                "operation": "investigate",
                "round_index": 1,
                "task": {
                    "role": AgentRole.D5,
                    "question": "Check the recorded recipient preference for this message.",
                    "reason": "A cited code path should authorize the bounded read.",
                },
            }
        )


def test_migration_has_durable_control_and_source_tables() -> None:
    migration = (
        Path(__file__).resolve().parents[1]
        / "supabase/migrations/202610200001_incident_investigator.sql"
    ).read_text()
    for table in (
        "incident.cases",
        "incident.agent_runs",
        "incident.tool_calls",
        "incident.evidence",
        "incident.findings",
        "incident.report_revisions",
        "incident.demo_source_records",
    ):
        assert table in migration
