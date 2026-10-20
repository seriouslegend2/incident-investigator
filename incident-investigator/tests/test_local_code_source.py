from __future__ import annotations

from pathlib import Path

import pytest

from app.tools.local_code import LocalCodeSearch, TopologyIndex


@pytest.mark.asyncio
async def test_local_code_search_reads_only_approved_demo_roots() -> None:
    root = Path(__file__).resolve().parents[1]
    source = LocalCodeSearch(
        repository_root=root / "example-systems/opentelemetry-demo",
        deployment_fixture_root=root / "demo-fixtures/deployments",
    )
    results = await source.search("checkout email delivery", limit=12)

    assert results
    assert all(item["source_record_id"].startswith("local-") for item in results)
    assert all("source_group=" in item["content"] for item in results)
    assert any("delivery_events" in item["content"] for item in results)


@pytest.mark.asyncio
async def test_topology_index_returns_candidate_paths_not_raw_archive() -> None:
    root = Path(__file__).resolve().parents[1]
    source = LocalCodeSearch(
        repository_root=root / "example-systems/opentelemetry-demo",
        deployment_fixture_root=root / "demo-fixtures/deployments",
    )

    scope = await TopologyIndex(source).resolve("order confirmation email")

    assert scope["candidate_paths"]
    assert len(scope["candidate_paths"]) <= 8
    assert "checkout" in scope["candidate_services"]
