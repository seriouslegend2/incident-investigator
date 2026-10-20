from __future__ import annotations

from ...models import AgentRole
from ..contracts import AgentDefinition
from .executor import build_d5
from .models import D5InvestigateInput, D5InvestigateOutput

agent_definition = AgentDefinition(
    name=AgentRole.D5,
    description="Read-replica/history evidence specialist; only runs with a D4 ReadContract.",
    default_model="gpt-4.1-mini",
    prompt_version="d5-data-v1",
    allowed_tools=(
        "describe_authorized_projection",
        "lookup_contract_row",
        "get_contract_history",
    ),
    operations={"investigate": (D5InvestigateInput, D5InvestigateOutput)},
    build=build_d5,
)
