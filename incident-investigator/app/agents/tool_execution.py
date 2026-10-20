from __future__ import annotations

from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from ..models import AgentRole, EvidenceRecord
from ..tools.contracts import EvidenceSearchOutput
from .contracts import AgentInvocation
from .runtime import AgentRuntime

OutputModel = TypeVar("OutputModel", bound=BaseModel)


class ToolProtocolError(RuntimeError):
    pass


async def run_required_tool_then_structure(
    *,
    runtime: AgentRuntime,
    invocation: AgentInvocation,
    system_prompt: str,
    user_prompt: str,
    tools: list[BaseTool],
    output_model: type[OutputModel],
    role: AgentRole,
    operation: str,
    max_tool_calls: int,
) -> tuple[OutputModel, list[EvidenceRecord]]:
    """Run a bounded family of source tools, then require a citation-bounded structured result."""

    if not tools:
        raise ToolProtocolError(f"{role.value} has no tools for this operation")
    tools_by_name = {tool.name: tool for tool in tools}
    model = runtime.model()
    trace_config = runtime.trace_config(invocation, role, operation)
    messages = [SystemMessage(system_prompt), HumanMessage(user_prompt)]
    tool_model = model.bind_tools(tools, tool_choice="required")
    response = await tool_model.ainvoke(messages, config=trace_config)
    if not response.tool_calls:
        raise ToolProtocolError(f"{role.value} did not make its required evidence tool call")
    if len(response.tool_calls) > max_tool_calls:
        raise ToolProtocolError(
            f"{role.value} requested more than {max_tool_calls} bounded tool calls"
        )

    tool_messages: list[ToolMessage] = []
    evidence: list[EvidenceRecord] = []
    for call in response.tool_calls:
        tool = tools_by_name.get(call["name"])
        if tool is None:
            raise ToolProtocolError(f"{role.value} requested disallowed tool {call['name']!r}")
        output = await tool.ainvoke(call["args"], config=trace_config)
        parsed = EvidenceSearchOutput.model_validate_json(output)
        evidence.extend(parsed.evidence)
        tool_messages.append(ToolMessage(content=output, tool_call_id=call["id"]))

    structured = model.with_structured_output(output_model, method="json_schema")
    structure_messages = [*messages, response, *tool_messages]
    available_ids = ", ".join(item.evidence_id for item in evidence) or "none"
    for attempt in range(2):
        result = await structured.ainvoke(structure_messages, config=trace_config)
        try:
            # Every current specialist analysis exposes evidence_ids. Keep this generic helper
            # defensive so a future non-evidence output model can still use it.
            validate_evidence_citations(list(getattr(result, "evidence_ids", [])), evidence)
            return result, evidence
        except ToolProtocolError:
            if attempt == 1:
                raise
            structure_messages = [
                *structure_messages,
                HumanMessage(
                    "Your draft cited an evidence ID that was not returned by your tools. "
                    f"Return a corrected structured result using only these IDs: {available_ids}. "
                    "Do not make another tool call or add facts."
                ),
            ]
    raise AssertionError("unreachable citation-correction loop")


def validate_evidence_citations(citations: list[str], evidence: list[EvidenceRecord]) -> None:
    available = {item.evidence_id for item in evidence}
    unknown = set(citations) - available
    if unknown:
        raise ToolProtocolError(
            "Agent cited evidence it did not obtain through its tool: " + ", ".join(sorted(unknown))
        )
