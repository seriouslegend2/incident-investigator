from __future__ import annotations

from ...models import AgentRole
from ..contracts import AgentDefinition
from .executor import build_d3
from .models import D3InvestigateInput, D3InvestigateOutput

agent_definition = AgentDefinition(
    name=AgentRole.D3,
    description="Logs, traces, metrics and provider-outcome evidence specialist.",
    default_model="gpt-4.1-mini",
    prompt_version="d3-observability-v2",
    allowed_tools=("find_trace_or_request", "search_log_slice", "get_metric_or_provider_window"),
    operations={"investigate": (D3InvestigateInput, D3InvestigateOutput)},
    build=build_d3,
)
