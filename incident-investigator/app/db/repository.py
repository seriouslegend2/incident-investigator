from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from ..models import (
    AgentFinding,
    AgentRole,
    CaseScope,
    CaseStatus,
    EvidenceRecord,
    IncidentCase,
    IncidentReport,
)
from .database import Database


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentRepository:
    """Durable case/evidence ledger and the seeded-source read boundary."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def create_case(self, case: IncidentCase) -> None:
        await self._database.pool.execute(
            """
            insert into incident.cases
              (case_id, complaint, scenario_id, tenant_id, requested_by, status, created_at, updated_at)
            values ($1, $2, $3, $4, $5, $6, $7, $7)
            """,
            case.case_id,
            case.complaint,
            case.scope.scenario_id,
            case.scope.tenant_id,
            case.requested_by,
            case.status.value,
            case.created_at,
        )

    async def get_case(self, case_id: str) -> IncidentCase | None:
        row = await self._database.pool.fetchrow(
            """select case_id, complaint, scenario_id, tenant_id, requested_by, status, created_at
               from incident.cases where case_id = $1""",
            case_id,
        )
        if row is None:
            return None
        return IncidentCase(
            case_id=row["case_id"],
            complaint=row["complaint"],
            scope=CaseScope(scenario_id=row["scenario_id"], tenant_id=row["tenant_id"]),
            requested_by=row["requested_by"],
            status=CaseStatus(row["status"]),
            created_at=row["created_at"],
        )

    async def update_case_status(self, case_id: str, status: CaseStatus) -> None:
        await self._database.pool.execute(
            "update incident.cases set status = $2, updated_at = $3 where case_id = $1",
            case_id,
            status.value,
            _utc_now(),
        )

    async def list_scenarios(self) -> list[dict[str, str]]:
        rows = await self._database.pool.fetch(
            "select scenario_id, title, description from incident.demo_scenarios order by scenario_id"
        )
        return [dict(row) for row in rows]

    async def scenario_exists(self, scenario_id: str) -> bool:
        return bool(
            await self._database.pool.fetchval(
                "select exists(select 1 from incident.demo_scenarios where scenario_id = $1)",
                scenario_id,
            )
        )

    async def begin_agent_run(
        self,
        *,
        run_id: str,
        case_id: str,
        task_id: str,
        role: AgentRole,
        operation: str,
        model_name: str,
        input_json: dict[str, Any],
    ) -> None:
        await self._database.pool.execute(
            """
            insert into incident.agent_runs
              (run_id, case_id, task_id, role, operation, model_name, langsmith_run_name, status, input_json)
            values ($1, $2, $3, $4, $5, $6, $7, 'started', $8::jsonb)
            """,
            run_id,
            case_id,
            task_id,
            role.value,
            operation,
            model_name,
            f"incident/{role.value.lower()}/{operation}",
            json.dumps(input_json, default=str),
        )

    async def finish_agent_run(
        self,
        run_id: str,
        *,
        output_json: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        status = "failed" if error_message else "succeeded"
        await self._database.pool.execute(
            """
            update incident.agent_runs
            set status = $2, output_json = $3::jsonb, error_message = $4, completed_at = $5
            where run_id = $1
            """,
            run_id,
            status,
            json.dumps(output_json or {}, default=str),
            error_message,
            _utc_now(),
        )

    async def record_tool_call(
        self,
        *,
        tool_call_id: str,
        case_id: str,
        task_id: str,
        run_id: str,
        role: AgentRole,
        tool_name: str,
        arguments: dict[str, Any],
        status: str,
        result_count: int,
    ) -> None:
        await self._database.pool.execute(
            """
            insert into incident.tool_calls
              (tool_call_id, case_id, task_id, run_id, role, tool_name, arguments_json, status, result_count)
            values ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9)
            """,
            tool_call_id,
            case_id,
            task_id,
            run_id,
            role.value,
            tool_name,
            json.dumps(arguments),
            status,
            result_count,
        )

    async def record_evidence(
        self, record: EvidenceRecord, *, case_id: str, tool_call_id: str
    ) -> None:
        await self._database.pool.execute(
            """
            insert into incident.evidence
              (evidence_id, case_id, tool_call_id, source_kind, source_record_id, observed_at,
               summary, coverage_note, content, metadata)
            values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb)
            """,
            record.evidence_id,
            case_id,
            tool_call_id,
            record.source_kind,
            record.source_record_id,
            record.observed_at,
            record.summary,
            record.coverage_note,
            record.content,
            json.dumps(record.metadata),
        )

    async def get_case_evidence(
        self, *, case_id: str, evidence_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Return only already-cited evidence from this case for independent review."""

        if not evidence_ids:
            return []
        rows = await self._database.pool.fetch(
            """
            select evidence_id, source_kind, source_record_id, summary, content, coverage_note
            from incident.evidence
            where case_id = $1 and evidence_id = any($2::text[])
            order by created_at asc
            """,
            case_id,
            list(dict.fromkeys(evidence_ids))[:40],
        )
        return [dict(row) for row in rows]

    async def search_demo_source(
        self,
        *,
        scenario_id: str,
        source_kind: str,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Bounded parameterized search; schema/table/tenant never comes from model input."""

        tokens = list(dict.fromkeys(re.findall(r"[a-zA-Z0-9_-]{3,}", query.lower())))[:8]
        if not tokens:
            return []
        rows = await self._database.pool.fetch(
            """
            select source_record_id, source_kind, observed_at, summary, content, coverage_note, metadata
            from incident.demo_source_records
            where scenario_id = $1
              and source_kind = $2
              and exists (
                select 1 from unnest($3::text[]) as token
                where lower(summary || ' ' || content) like '%' || token || '%'
              )
            order by observed_at desc
            limit $4
            """,
            scenario_id,
            source_kind,
            tokens,
            limit,
        )
        return [dict(row) for row in rows]

    async def save_finding(self, *, case_id: str, task_id: str, finding: AgentFinding) -> None:
        await self._database.pool.execute(
            """
            insert into incident.findings (finding_id, case_id, task_id, role, finding_json)
            values ($1, $2, $3, $4, $5::jsonb)
            """,
            finding.finding_id,
            case_id,
            task_id,
            finding.role.value,
            finding.model_dump_json(),
        )

    async def save_report(self, report_id: str, report: IncidentReport) -> None:
        await self._database.pool.execute(
            """
            insert into incident.report_revisions (report_id, case_id, report_json, d7_approved)
            values ($1, $2, $3::jsonb, $4)
            """,
            report_id,
            report.case_id,
            report.model_dump_json(),
            report.reviewed_by_d7,
        )

    async def latest_report(self, case_id: str) -> IncidentReport | None:
        row = await self._database.pool.fetchrow(
            """
            select report_json from incident.report_revisions
            where case_id = $1 order by created_at desc limit 1
            """,
            case_id,
        )
        if row is None:
            return None
        payload = row["report_json"]
        return IncidentReport.model_validate(
            json.loads(payload) if isinstance(payload, str) else payload
        )
