from __future__ import annotations

from langchain_core.tools import BaseTool

from ...models import AgentRole
from ...tools.gateway import make_evidence_tool
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime


def build_tools(invocation: AgentInvocation, runtime: AgentRuntime) -> list[BaseTool]:
    return [
        make_evidence_tool(
            name="find_trace_or_request",
            description="Find bounded trace/request/correlation evidence inside the trusted case scope.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D3,
            source_kind="observability",
        ),
        make_evidence_tool(
            name="search_log_slice",
            description="Search a bounded case-scoped log slice; do not request broad archives.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D3,
            source_kind="observability",
        ),
        make_evidence_tool(
            name="get_metric_or_provider_window",
            description="Retrieve bounded metric, provider-outcome or queue-window evidence for this case.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D3,
            source_kind="observability",
        ),
    ]
