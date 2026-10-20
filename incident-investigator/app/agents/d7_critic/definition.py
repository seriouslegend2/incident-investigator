from __future__ import annotations

from ...models import AgentRole
from ..contracts import AgentDefinition
from .executor import build_d7
from .models import D7ReportReviewInput, D7ReportReviewOutput, D7ReviewInput, D7ReviewOutput

agent_definition = AgentDefinition(
    name=AgentRole.D7,
    description="Independent critic for evidence claims and the final report gate.",
    default_model="gpt-4.1-mini",
    prompt_version="d7-critic-v1",
    allowed_tools=(),
    operations={
        "review": (D7ReviewInput, D7ReviewOutput),
        "review_report": (D7ReportReviewInput, D7ReportReviewOutput),
    },
    build=build_d7,
)
