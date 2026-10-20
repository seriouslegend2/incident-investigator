# ruff: noqa: E402
from __future__ import annotations

import argparse
import asyncio
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

# Allow the documented `uv run python scripts/...` commands to import the
# application package when Python sets sys.path to the scripts directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agents.runtime import AgentRuntime
from app.config import get_settings
from app.db.database import Database
from app.db.repository import IncidentRepository
from app.models import CaseScope, CaseStatus, IncidentCase
from app.tools.gateway import ToolGateway
from app.tools.local_code import LocalCodeSearch
from app.workflows.graph import investigate


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run one real, traced demo investigation")
    parser.add_argument("scenario_id")
    parser.add_argument("complaint")
    args = parser.parse_args()

    settings = get_settings()
    settings.require_agent_runtime()
    database = Database(settings.database_url.get_secret_value())
    await database.connect()
    try:
        repository = IncidentRepository(database)
        if not await repository.scenario_exists(args.scenario_id):
            raise ValueError("Unknown scenario; run scripts/seed_demo.py first")
        runtime = AgentRuntime(
            settings=settings,
            repository=repository,
            gateway=ToolGateway(
                repository=repository,
                max_rows=settings.max_tool_rows,
                local_code=LocalCodeSearch(
                    repository_root=settings.reference_repository_path,
                    deployment_fixture_root=settings.deployment_fixture_path,
                ),
            ),
        )
        case = IncidentCase(
            case_id=f"case_{uuid.uuid4().hex}",
            complaint=args.complaint,
            scope=CaseScope(scenario_id=args.scenario_id),
            requested_by="cli-demo",
            status=CaseStatus.OPEN,
            created_at=datetime.now(UTC),
        )
        await repository.create_case(case)
        report = await investigate(case, runtime)
        print(report.model_dump_json(indent=2))
        trace_url = runtime.get_case_trace_url(case.case_id)
        if trace_url:
            print(f"\nLangSmith trace: {trace_url}")
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())
