from __future__ import annotations

from ...models import AgentRole
from ..contracts import AgentDefinition
from .executor import build_d4
from .models import D4InvestigateInput, D4InvestigateOutput

agent_definition = AgentDefinition(
    name=AgentRole.D4,
    description="Repository, deployment and configuration evidence specialist; can propose a bounded data ReadContract.",
    default_model="gpt-4.1-mini",
    prompt_version="d4-code-deploy-v2",
    allowed_tools=(
        "map_service_path",
        "search_code_symbols",
        "read_source_range",
        "get_deployment_or_config_diff",
    ),
    operations={"investigate": (D4InvestigateInput, D4InvestigateOutput)},
    build=build_d4,
)
