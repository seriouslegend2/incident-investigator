from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status

from .agents.registry import discover_agents
from .agents.runtime import AgentRuntime
from .config import Settings, get_settings
from .db.database import Database
from .db.repository import IncidentRepository
from .models import (
    CaseScope,
    CaseStatus,
    CreateInvestigationRequest,
    IncidentCase,
    InvestigationResponse,
)
from .tools.gateway import ToolGateway
from .tools.local_code import LocalCodeSearch
from .workflows.graph import investigate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.settings = settings
    app.state.runtime = None
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
    return InvestigationResponse(case=refreshed_case or case, report=report)


@app.get("/api/investigations/{case_id}", response_model=InvestigationResponse)
async def get_investigation(case_id: str, request: Request) -> InvestigationResponse:
    runtime = _runtime(request)
    case = await runtime.repository.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Investigation case not found.")
    return InvestigationResponse(case=case, report=await runtime.repository.latest_report(case_id))
