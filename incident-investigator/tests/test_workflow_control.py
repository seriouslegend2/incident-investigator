from __future__ import annotations

from app.models import AgentRole, SpecialistTask
from app.workflows.graph import after_specialist, dispatch_from_d1


def _task() -> SpecialistTask:
    return SpecialistTask(
        role=AgentRole.D3,
        question="Find the request trace for order-42.",
        reason="The customer complaint names a missing confirmation email.",
    )


def test_d1_selected_tasks_form_one_batch_before_d7_review() -> None:
    """A specialist result must not cause an independent D1 replanning pass."""

    state = {"next_action": "dispatch", "pending_tasks": [_task(), _task()]}
    assert dispatch_from_d1(state) == "run_specialist"
    assert after_specialist({"pending_tasks": [_task()]}) == "run_specialist"
    assert after_specialist({"pending_tasks": []}) == "d7_review"


def test_d1_can_hand_a_case_to_d7_without_specialist_dispatch() -> None:
    assert dispatch_from_d1({"next_action": "critic", "pending_tasks": []}) == "d7_review"
