from __future__ import annotations

from langchain_core.tools import BaseTool

from ...models import AgentRole
from ...tools.gateway import make_evidence_tool
from ..contracts import AgentInvocation
from ..runtime import AgentRuntime


def build_tools(invocation: AgentInvocation, runtime: AgentRuntime) -> list[BaseTool]:
    if invocation.read_contract is None:
        raise PermissionError("D5 tool construction requires a D4 ReadContract")
    return [
        make_evidence_tool(
            name="describe_authorized_projection",
            description="Describe the exact backend-approved relation, lookup and fields in the supplied ReadContract.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D5,
            source_kind="data",
            read_contract=invocation.read_contract,
            backend="contract_description",
        ),
        make_evidence_tool(
            name="lookup_contract_row",
            description="Read bounded rows only through the supplied ReadContract; no SQL or table names are accepted.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D5,
            source_kind="data",
            read_contract=invocation.read_contract,
        ),
        make_evidence_tool(
            name="get_contract_history",
            description="Read bounded related history only through the supplied ReadContract.",
            gateway=runtime.gateway,
            invocation=invocation,
            role=AgentRole.D5,
            source_kind="data",
            read_contract=invocation.read_contract,
        ),
    ]
