from __future__ import annotations

from pathlib import Path

from app.agents.registry import discover_agents
from app.models import AgentRole


def test_exact_individual_agent_roster_and_no_d2() -> None:
    agents = discover_agents()
    assert set(agents) == {
        AgentRole.D1,
        AgentRole.D3,
        AgentRole.D4,
        AgentRole.D5,
        AgentRole.D6,
        AgentRole.D7,
        AgentRole.D8,
    }
    assert "D2" not in {role.value for role in agents}


def test_every_agent_has_its_own_kookar_style_package_files() -> None:
    root = Path(__file__).resolve().parents[1] / "app/agents"
    for directory in (
        "d1_orchestrator",
        "d3_observability",
        "d4_code_deploy",
        "d5_data",
        "d6_ai_behavior",
        "d7_critic",
        "d8_reporter",
    ):
        agent_dir = root / directory
        for filename in ("__init__.py", "definition.py", "models.py", "prompt.py", "executor.py"):
            assert (agent_dir / filename).is_file(), f"missing {directory}/{filename}"
    for directory in ("d3_observability", "d4_code_deploy", "d5_data", "d6_ai_behavior"):
        assert (root / directory / "tools.py").is_file()


def test_tool_permissions_are_role_specific() -> None:
    agents = discover_agents()
    assert agents[AgentRole.D1].allowed_tools == (
        "resolve_feature_scope",
        "expand_dependency_path",
    )
    assert agents[AgentRole.D3].allowed_tools == (
        "find_trace_or_request",
        "search_log_slice",
        "get_metric_or_provider_window",
    )
    assert agents[AgentRole.D4].allowed_tools == (
        "map_service_path",
        "search_code_symbols",
        "read_source_range",
        "get_deployment_or_config_diff",
    )
    assert agents[AgentRole.D5].allowed_tools == (
        "describe_authorized_projection",
        "lookup_contract_row",
        "get_contract_history",
    )
    assert agents[AgentRole.D6].allowed_tools == (
        "get_ai_run_trace",
        "get_prompt_snapshot",
        "get_retrieval_snapshot",
        "get_tool_handoff_timeline",
    )
    assert agents[AgentRole.D7].allowed_tools == ()
    assert agents[AgentRole.D8].allowed_tools == ()
