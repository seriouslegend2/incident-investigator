from __future__ import annotations

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from .agents.registry import discover_agents
from .agents.runtime import AgentRuntime
from .config import Settings, get_settings
from .db.database import Database
from .db.repository import IncidentRepository
from .demo_page import DEMO_PAGE
from .models import (
    CaseScope,
    CaseStatus,
    CreateInvestigationRequest,
    IncidentCase,
    InvestigationResponse,
    InvestigationStartResponse,
)
from .tools.gateway import ToolGateway
from .tools.local_code import LocalCodeSearch
from .workflows.graph import investigate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.configure_langsmith_runtime()
    app.state.settings = settings
    app.state.runtime = None
    app.state.demo_tasks = set()
    if settings.database_url is not None:
        database = Database(settings.database_url.get_secret_value())
        await database.connect()
        repository = IncidentRepository(database)
        app.state.runtime = AgentRuntime(
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
    try:
        yield
    finally:
        runtime: AgentRuntime | None = app.state.runtime
        if runtime is not None:
            await runtime.repository._database.close()  # noqa: SLF001 - app owns lifecycle here


app = FastAPI(
    title="Incident Investigator",
    version="0.1.0",
    description="OpenAI tool-grounded multi-agent incident investigation demo.",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def live_demo_page() -> HTMLResponse:
    """A minimal presentation surface for the live API; no fixture conclusions are rendered."""

    return HTMLResponse(DEMO_PAGE)


def _runtime(request: Request) -> AgentRuntime:
    runtime: AgentRuntime | None = request.app.state.runtime
    if runtime is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DATABASE_URL is required; run migrations and seed demo data before using the API.",
        )
    if not runtime.settings.can_run_agents:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is required for real agent execution.",
        )
    return runtime


@app.get("/health")
async def health(request: Request) -> dict[str, object]:
    settings: Settings = request.app.state.settings
    return {
        "status": "ok",
        "database_configured": settings.database_url is not None,
        "openai_configured": settings.openai_api_key is not None,
        "langsmith_enabled": settings.langsmith_tracing,
        "agents": [role.value for role in discover_agents()],
    }


@app.get("/api/demo/scenarios")
async def demo_scenarios(request: Request) -> list[dict[str, str]]:
    runtime = _runtime(request)
    return await runtime.repository.list_scenarios()


@app.post(
    "/api/investigations",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_investigation(
    payload: CreateInvestigationRequest,
    request: Request,
) -> InvestigationResponse:
    runtime = _runtime(request)
    if not await runtime.repository.scenario_exists(payload.scenario_id):
        raise HTTPException(status_code=404, detail="Unknown seeded demo scenario.")
    case = IncidentCase(
        case_id=f"case_{uuid.uuid4().hex}",
        complaint=payload.complaint,
        scope=CaseScope(scenario_id=payload.scenario_id),
        requested_by=payload.requested_by,
        status=CaseStatus.OPEN,
        created_at=datetime.now(UTC),
    )
    await runtime.repository.create_case(case)
    try:
        report = await investigate(case, runtime)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Investigation run failed: {exc}") from exc
    refreshed_case = await runtime.repository.get_case(case.case_id)
    return InvestigationResponse(
        case=refreshed_case or case,
        report=report,
        trace_url=runtime.get_case_trace_url(case.case_id),
    )


@app.post(
    "/api/investigations/start",
    response_model=InvestigationStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_investigation(
    payload: CreateInvestigationRequest,
    request: Request,
) -> InvestigationStartResponse:
    """Start a real run in the background so the demo page can show durable receipts live."""

    runtime = _runtime(request)
    if not await runtime.repository.scenario_exists(payload.scenario_id):
        raise HTTPException(status_code=404, detail="Unknown seeded demo scenario.")
    case = IncidentCase(
        case_id=f"case_{uuid.uuid4().hex}",
        complaint=payload.complaint,
        scope=CaseScope(scenario_id=payload.scenario_id),
        requested_by=payload.requested_by,
        status=CaseStatus.OPEN,
        created_at=datetime.now(UTC),
    )
    await runtime.repository.create_case(case)

    async def run_case() -> None:
        try:
            await investigate(case, runtime)
        except Exception:
            # investigate() writes the failed case status. The UI reads it through the normal API.
            return

    task = asyncio.create_task(run_case(), name=f"incident-demo-{case.case_id}")
    request.app.state.demo_tasks.add(task)
    task.add_done_callback(request.app.state.demo_tasks.discard)
    return InvestigationStartResponse(case=case)


@app.get("/api/investigations/{case_id}", response_model=InvestigationResponse)
async def get_investigation(case_id: str, request: Request) -> InvestigationResponse:
    runtime = _runtime(request)
    case = await runtime.repository.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Investigation case not found.")
    return InvestigationResponse(
        case=case,
        report=await runtime.repository.latest_report(case_id),
        trace_url=runtime.get_case_trace_url(case_id),
    )


@app.get("/api/investigations/{case_id}/timeline")
async def get_investigation_timeline(case_id: str, request: Request) -> list[dict[str, object]]:
    runtime = _runtime(request)
    if await runtime.repository.get_case(case_id) is None:
        raise HTTPException(status_code=404, detail="Unknown investigation case.")
    return [
        event.model_dump(mode="json")
        for event in await runtime.repository.get_case_timeline(case_id)
    ]
