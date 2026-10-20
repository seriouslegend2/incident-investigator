from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.agents.d1_orchestrator.models import D1PlanOutput
from app.models import AgentRole, SpecialistTask
from app.workflows.graph import PARALLEL_SPECIALIST_NODES, dispatch_from_d1, run_specialist_for_role


def _task() -> SpecialistTask:
    return SpecialistTask(
        role=AgentRole.D3,
        question="Find the request trace for order-42.",
        reason="The customer complaint names a missing confirmation email.",
    )


def test_d1_selected_tasks_fan_out_to_a_fixed_join_batch() -> None:
    """A selected batch starts parallel role branches, not sequential D1 replans."""

    state = {"next_action": "dispatch", "pending_tasks": [_task()]}
    assert set(dispatch_from_d1(state)) == set(PARALLEL_SPECIALIST_NODES.values())


def test_d1_can_hand_a_case_to_d7_without_specialist_dispatch() -> None:
    assert dispatch_from_d1({"next_action": "critic", "pending_tasks": []}) == "d7_review"


@pytest.mark.asyncio
async def test_unselected_parallel_role_is_a_true_no_op() -> None:
    result = await run_specialist_for_role(
        {"pending_tasks": [_task()]},
        runtime=None,  # type: ignore[arg-type]  # Must not be accessed for a no-op branch.
        role=AgentRole.D4,
    )
    assert result == {}


def test_d1_parallel_batch_rejects_duplicate_specialist_roles() -> None:
    with pytest.raises(ValidationError, match="at most one task per specialist"):
        D1PlanOutput(
            next_action="dispatch",
            rationale="Two tasks would race through the same specialist branch.",
            tasks=[_task(), _task()],
        )
