from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict

from ..agents.d1_orchestrator.models import D1PlanOutput
from ..agents.d7_critic.models import D7ReportReviewOutput, D7ReviewOutput
from ..agents.d8_reporter.models import D8DraftOutput
from ..models import AgentFinding, IncidentCase, IncidentReport, ReadContract, SpecialistTask


class InvestigationState(TypedDict, total=False):
    case: IncidentCase
    round_index: int
    pending_tasks: list[SpecialistTask]
    next_action: Literal["dispatch", "critic", "replan", "write", "deliver", "withhold"]
    findings: Annotated[list[AgentFinding], operator.add]
    read_contract: ReadContract
    critic_followup_count: int
    critic_followup_limit: int
    requested_follow_up_tasks: list[SpecialistTask]
    d1_plan: D1PlanOutput
    d7_review: D7ReviewOutput
    d7_report_review: D7ReportReviewOutput
    d8_draft: D8DraftOutput
    report: IncidentReport
