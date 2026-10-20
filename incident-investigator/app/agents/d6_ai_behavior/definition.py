from __future__ import annotations

from ...models import AgentRole
from ..contracts import AgentDefinition
from .executor import build_d6
from .models import D6InvestigateInput, D6InvestigateOutput

agent_definition = AgentDefinition(
    name=AgentRole.D6,
    description="Observed prompt/retrieval/tool/handoff evidence specialist.",
    default_model="gpt-4.1-mini",
    prompt_version="d6-ai-behavior-v2",
    allowed_tools=(
        "get_ai_run_trace",
        "get_prompt_snapshot",
        "get_retrieval_snapshot",
        "get_tool_handoff_timeline",
    ),
    operations={"investigate": (D6InvestigateInput, D6InvestigateOutput)},
    build=build_d6,
)
