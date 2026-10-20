from __future__ import annotations

from ...models import AgentRole
from ..contracts import AgentDefinition
from .executor import build_d8
from .models import D8DraftOutput, D8WriteInput

agent_definition = AgentDefinition(
    name=AgentRole.D8,
    description="Evidence-cited incident report writer; has no source tools.",
    default_model="gpt-4.1-mini",
    prompt_version="d8-reporter-v1",
    allowed_tools=(),
    operations={"write": (D8WriteInput, D8DraftOutput)},
    build=build_d8,
)
