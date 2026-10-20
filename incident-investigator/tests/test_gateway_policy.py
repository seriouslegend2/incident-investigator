from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.agents.contracts import AgentInvocation
from app.models import AgentRole, CaseScope, CaseStatus, IncidentCase
from app.tools.gateway import ToolGateway


class NoReadRepository:
    async def search_demo_source(self, **kwargs):  # pragma: no cover - must not be called
        raise AssertionError(f"source access should have been denied: {kwargs}")


def _invocation() -> AgentInvocation:
    return AgentInvocation(
        case=IncidentCase(
            case_id="case_test",
            complaint="A customer says a reminder did not arrive.",
            scope=CaseScope(scenario_id="message-reminder"),
            requested_by="test",
            status=CaseStatus.OPEN,
            created_at=datetime.now(UTC),
        ),
        task_id="task_test",
        run_id="run_test",
        operation="investigate",
        round_index=1,
    )


@pytest.mark.asyncio
async def test_role_cannot_cross_source_boundary() -> None:
    gateway = ToolGateway(repository=NoReadRepository(), max_rows=3)  # type: ignore[arg-type]
    with pytest.raises(PermissionError, match="cannot read data"):
        await gateway.search(
            invocation=_invocation(),
            role=AgentRole.D3,
            source_kind="data",
            tool_name="not_allowed",
            query="customer preference",
        )


@pytest.mark.asyncio
async def test_d5_cannot_read_without_contract() -> None:
    gateway = ToolGateway(repository=NoReadRepository(), max_rows=3)  # type: ignore[arg-type]
    with pytest.raises(PermissionError, match="ReadContract"):
        await gateway.search(
            invocation=_invocation(),
            role=AgentRole.D5,
            source_kind="data",
            tool_name="read_contract_scoped_data",
            query="customer preference",
        )
