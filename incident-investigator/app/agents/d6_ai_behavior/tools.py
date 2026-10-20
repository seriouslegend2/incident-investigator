from __future__ import annotations

from langchain_core.tools import BaseTool

from ...models import AgentRole
from ...tools.gateway import make_evidence_tool
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime


def build_tools(invocation: AgentInvocation, runtime: AgentRuntime) -> list[BaseTool]:
    return [
        make_evidence_tool(
            name="get_ai_run_trace",
            description="Find bounded AI run and correlation-trace records in the trusted case scope.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D6,
            source_kind="ai_runtime",
        ),
        make_evidence_tool(
            name="get_prompt_snapshot",
            description="Retrieve observed prompt-version metadata from bounded AI runtime evidence.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D6,
            source_kind="ai_runtime",
        ),
        make_evidence_tool(
            name="get_retrieval_snapshot",
            description="Retrieve observed retrieval-context metadata from bounded AI runtime evidence.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D6,
            source_kind="ai_runtime",
        ),
        make_evidence_tool(
            name="get_tool_handoff_timeline",
            description="Retrieve bounded observed AI tool-call and handoff events.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D6,
            source_kind="ai_runtime",
        ),
    ]
