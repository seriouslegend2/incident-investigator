from __future__ import annotations

from langchain_core.tools import BaseTool, StructuredTool

from ...tools.contracts import EvidenceSearchInput, ScopeLookupOutput
from ...tools.local_code import TopologyIndex
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime


def build_tools(invocation: AgentInvocation, runtime: AgentRuntime) -> list[BaseTool]:
    if runtime.gateway.local_code is None:
        raise RuntimeError("D1 topology index requires the approved local source connector")
    index = TopologyIndex(runtime.gateway.local_code)

    async def resolve_feature_scope(query: str) -> str:
        result = await index.resolve(query)
        return ScopeLookupOutput.model_validate(result).model_dump_json()

    async def expand_dependency_path(query: str) -> str:
        result = await index.resolve(query)
        return ScopeLookupOutput.model_validate(result).model_dump_json()

    return [
        StructuredTool.from_function(
            coroutine=resolve_feature_scope,
            name="resolve_feature_scope",
            description=(
                "Return a small candidate service/path scope for the complaint. It is a routing "
                "hint from the approved index, not incident evidence."
            ),
            args_schema=EvidenceSearchInput,
        ),
        StructuredTool.from_function(
            coroutine=expand_dependency_path,
            name="expand_dependency_path",
            description=(
                "Expand one candidate workflow/dependency path using the approved index. "
                "It returns only candidate services and paths, not raw source or logs."
            ),
            args_schema=EvidenceSearchInput,
        ),
    ]
