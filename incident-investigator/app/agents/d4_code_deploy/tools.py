from __future__ import annotations

from langchain_core.tools import BaseTool

from ...models import AgentRole
from ...tools.gateway import make_evidence_tool
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime


def build_tools(invocation: AgentInvocation, runtime: AgentRuntime) -> list[BaseTool]:
    return [
        make_evidence_tool(
            name="map_service_path",
            description="Map a feature to candidate services and paths in the approved local source roots.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D4,
            source_kind="code_deploy",
            backend="local_code",
        ),
        make_evidence_tool(
            name="search_code_symbols",
            description="Search code symbols and identifiers in the approved local repository only.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D4,
            source_kind="code_deploy",
            backend="local_code",
        ),
        make_evidence_tool(
            name="read_source_range",
            description="Retrieve a small matching source/configuration range from approved local roots.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D4,
            source_kind="code_deploy",
            backend="local_code",
        ),
        make_evidence_tool(
            name="get_deployment_or_config_diff",
            description="Search approved deployment and non-secret configuration fixtures for this case.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D4,
            source_kind="code_deploy",
            backend="local_code",
        ),
    ]
