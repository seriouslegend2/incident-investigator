from __future__ import annotations

from app.agents.d7_critic.executor import _review_issues
from app.agents.d7_critic.models import D7ReviewOutput
from app.models import AgentRole, SpecialistTask


def test_withheld_d7_review_cannot_carry_follow_up_tasks() -> None:
    review = D7ReviewOutput(
        decision="withhold",
        rationale="No bounded source records were available.",
        follow_up_tasks=[
            SpecialistTask(
                role=AgentRole.D3,
                question="Search another bounded trace window for this request.",
                reason="The initial evidence lookup returned no records.",
            )
        ],
    )
    assert _review_issues(review, has_read_contract=False) == [
        "only request_follow_up may include follow-up tasks"
    ]


def test_d7_review_rejects_d5_follow_up_without_contract() -> None:
    review = D7ReviewOutput(
        decision="request_follow_up",
        rationale="One data lookup could change the conclusion.",
        follow_up_tasks=[
            SpecialistTask(
                role=AgentRole.D5,
                question="Check the data row required by the suspected code path.",
                reason="The current evidence does not establish the stored value.",
            )
        ],
    )
    assert _review_issues(review, has_read_contract=False) == [
        "D7 selected D5 without a D4 ReadContract"
    ]
