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
    TimelineEvent,
)
from .database import Database


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}
    return {}


def _brief(value: Any, *, limit: int = 260) -> str:
    text = str(value or "").strip()
    return text if len(text) <= limit else f"{text[: limit - 1].rstrip()}…"


def _agent_timeline_details(
    *,
    role: AgentRole,
    operation: str,
    status: str,
    input_json: dict[str, Any],
    output_json: dict[str, Any],
) -> tuple[str, str, str, list[str]]:
    """Summarize durable receipts for a presenter; never replay prompts or raw evidence."""

    findings = input_json.get("findings", [])
    task = _json_object(input_json.get("task"))
    complaint = _json_object(input_json.get("case")).get("complaint")
    if operation == "plan":
        input_summary = f"Complaint: {_brief(complaint)}"
    elif operation == "investigate":
        input_summary = f"Question: {_brief(task.get('question'))}"
    elif operation == "review":
        input_summary = f"Review {len(findings)} specialist finding(s) and their cited evidence."
    elif operation == "write":
        input_summary = f"Write a report from {len(findings)} D7-reviewed finding(s)."
    elif operation == "review_report":
        input_summary = "Check the exact D8 draft before it reaches the operator."
    else:
        input_summary = "Bounded case-scoped agent input."

    if status == "started":
        return input_summary, "Running…", "Wait for this bounded agent result.", []
    if status == "failed":
        return (
            input_summary,
            "Agent output was rejected by a safety or contract check.",
            "Recover safely: retry a bounded correction or withhold the case.",
            [],
        )

    if operation == "plan":
        tasks = output_json.get("tasks", [])
        task_summary = "; ".join(
            f"{item.get('role', 'specialist')}: {_brief(item.get('question'), limit=110)}"
            for item in tasks
            if isinstance(item, dict)
        )
        next_action = output_json.get("next_action")
        return (
            input_summary,
            f"Plan: {task_summary or 'no specialist task returned'}",
            (
                "Start selected specialists in parallel."
                if next_action == "dispatch"
                else "Send the current evidence state to D7 for review."
            ),
            [],
        )

    if operation == "investigate":
        finding = _json_object(output_json.get("finding"))
        evidence_ids = [str(item) for item in finding.get("evidence_ids", [])][:20]
        return (
            input_summary,
            f"Finding: {_brief(finding.get('answer') or 'No finding was returned.')}",
            "Join other selected specialist results, then let D7 challenge the combined evidence.",
            evidence_ids,
        )

    if operation in {"review", "review_report"}:
        decision = str(output_json.get("decision", "withhold"))
        rationale = _brief(output_json.get("rationale"))
        if operation == "review":
            next_step = {
                "approve": "Pass reviewed findings to D8.",
                "request_follow_up": "Send precise follow-up tasks back through D1.",
                "withhold": "Create a withheld/inconclusive operator report.",
            }.get(decision, "Withhold the case rather than invent a conclusion.")
        else:
            next_step = (
                "Release D8's exact approved report to the operator."
                if decision == "approve"
                else "Withhold the report because the final draft did not pass review."
            )
        return input_summary, f"Decision: {decision}. {rationale}", next_step, []

    if operation == "write":
        return (
            input_summary,
            f"Draft summary: {_brief(output_json.get('summary'))}",
            "D7 performs the final exact-draft delivery check.",
            [str(item) for item in output_json.get("evidence_ids", [])][:20],
        )

    return input_summary, "Agent response recorded.", "Continue the bounded workflow.", []


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

    async def get_case_timeline(self, case_id: str) -> list[TimelineEvent]:
        """Return a presentation-safe live timeline, never raw prompts or source content."""

        agent_rows = await self._database.pool.fetch(
            """
            select run_id, role, operation, status, input_json, output_json, started_at, completed_at
            from incident.agent_runs
            where case_id = $1
            order by started_at asc
            limit 100
            """,
            case_id,
        )
        tool_rows = await self._database.pool.fetch(
            """
            select tool_call_id, run_id, role, tool_name, arguments_json, status, result_count, created_at
            from incident.tool_calls
            where case_id = $1
            order by created_at asc
            limit 200
            """,
            case_id,
        )
        events = []
        for row in agent_rows:
            role = AgentRole(row["role"])
            input_summary, output_summary, next_step, evidence_ids = _agent_timeline_details(
                role=role,
                operation=row["operation"],
                status=row["status"],
                input_json=_json_object(row["input_json"]),
                output_json=_json_object(row["output_json"]),
            )
            events.append(
                TimelineEvent(
                    event_id=row["run_id"],
                    occurred_at=row["completed_at"] or row["started_at"],
                    kind="agent",
                    role=role,
                    label=f"{row['role']} · {row['operation']}",
                    status=row["status"],
                    input_summary=input_summary,
                    output_summary=output_summary,
                    next_step=next_step,
                    evidence_ids=evidence_ids,
                )
            )
        events.extend(
            TimelineEvent(
                event_id=row["tool_call_id"],
                parent_event_id=row["run_id"],
                occurred_at=row["created_at"],
                kind="tool",
                role=AgentRole(row["role"]),
                label=f"{row['role']} · {row['tool_name']}",
                status=row["status"],
                input_summary=(
                    f"Query: {_brief(_json_object(row['arguments_json']).get('query'))}"
                    if _json_object(row["arguments_json"]).get("query")
                    else "Bounded source query under this role's access policy."
                ),
                output_summary=f"{row['result_count']} bounded record(s) returned.",
                next_step=f"Return the bounded result to {row['role']} for its finding.",
            )
            for row in tool_rows
        )
        return sorted(events, key=lambda item: item.occurred_at)
