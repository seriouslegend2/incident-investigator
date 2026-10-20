# ruff: noqa: E402
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.db.database import Database


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show the durable, compact audit trail for one investigation case."
    )
    parser.add_argument("case_id")
    args = parser.parse_args()

    settings = get_settings()
    database = Database(settings.database_url.get_secret_value())
    await database.connect()
    try:
        case = await database.pool.fetchrow(
            """
            select case_id, scenario_id, status, created_at, updated_at
            from incident.cases where case_id = $1
            """,
            args.case_id,
        )
        if case is None:
            raise ValueError(f"Unknown case: {args.case_id}")
        agent_runs = await database.pool.fetch(
            """
            select run_id, role, operation, status, model_name, langsmith_run_name,
                   input_json #>> '{prompt,prompt_identifier}' as prompt_identifier,
                   input_json #>> '{prompt,prompt_version}' as prompt_version,
                   completed_at, error_message
            from incident.agent_runs
            where case_id = $1
            order by started_at
            """,
            args.case_id,
        )
        tool_calls = await database.pool.fetch(
            """
            select tool_call_id, role, tool_name, status, result_count, created_at
            from incident.tool_calls
            where case_id = $1
            order by created_at
            """,
            args.case_id,
        )
        evidence_count = await database.pool.fetchval(
            "select count(*) from incident.evidence where case_id = $1", args.case_id
        )
        report = await database.pool.fetchrow(
            """
            select report_json ->> 'status' as status, d7_approved, created_at
            from incident.report_revisions
            where case_id = $1
            order by created_at desc limit 1
            """,
            args.case_id,
        )
        print(
            json.dumps(
                {
                    "case": dict(case),
                    "agent_runs": [dict(row) for row in agent_runs],
                    "tool_calls": [dict(row) for row in tool_calls],
                    "evidence_count": evidence_count,
                    "latest_report": dict(report) if report is not None else None,
                },
                default=str,
                indent=2,
            )
        )
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())
