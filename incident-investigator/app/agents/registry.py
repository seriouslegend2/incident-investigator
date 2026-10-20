from __future__ import annotations

import importlib
import pkgutil
from functools import lru_cache

from ..models import AgentRole
from .contracts import AgentDefinition


@lru_cache
def discover_agents() -> dict[AgentRole, AgentDefinition]:
    """Discover package definitions, the Python equivalent of Kookar's generated worker registry."""

    package = importlib.import_module("app.agents")
    definitions: dict[AgentRole, AgentDefinition] = {}
    for candidate in pkgutil.iter_modules(package.__path__):
        if not candidate.ispkg or not candidate.name.startswith("d"):
            continue
        module = importlib.import_module(f"app.agents.{candidate.name}.definition")
        definition = getattr(module, "agent_definition", None)
        if not isinstance(definition, AgentDefinition):
            raise TypeError(f"{candidate.name} must export AgentDefinition as agent_definition")
        if definition.name in definitions:
            raise ValueError(f"Duplicate agent role: {definition.name.value}")
        definitions[definition.name] = definition

    expected = {
        AgentRole.D1,
        AgentRole.D3,
        AgentRole.D4,
        AgentRole.D5,
        AgentRole.D6,
        AgentRole.D7,
        AgentRole.D8,
    }
    if set(definitions) != expected:
        missing = ", ".join(role.value for role in sorted(expected - set(definitions), key=str))
        unexpected = ", ".join(role.value for role in sorted(set(definitions) - expected, key=str))
        raise RuntimeError(
            f"Agent registry mismatch; missing=[{missing}], unexpected=[{unexpected}]"
        )
    return definitions


def get_agent(role: AgentRole) -> AgentDefinition:
    return discover_agents()[role]
