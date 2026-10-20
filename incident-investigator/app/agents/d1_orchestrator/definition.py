from __future__ import annotations

from ...models import AgentRole
from ..contracts import AgentDefinition
from .executor import build_d1
from .models import D1PlanInput, D1PlanOutput

agent_definition = AgentDefinition(
    name=AgentRole.D1,
    description="Lead orchestrator that creates the next smallest evidence plan.",
    default_model="gpt-4.1-mini",
    prompt_version="d1-orchestrator-v3",
    allowed_tools=("resolve_feature_scope", "expand_dependency_path"),
    operations={"plan": (D1PlanInput, D1PlanOutput)},
    build=build_d1,
)
