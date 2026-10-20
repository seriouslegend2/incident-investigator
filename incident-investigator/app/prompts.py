from __future__ import annotations

import hashlib
import importlib
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from langsmith.utils import LangSmithConflictError

from .models import AgentRole


@dataclass(frozen=True)
class PromptSpec:
    identifier: str
    version: str
    description: str
    system_prompt: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.system_prompt.encode("utf-8")).hexdigest()


_PROMPT_DEFINITIONS: dict[tuple[AgentRole, str], tuple[str, str, str, str, str]] = {
    (AgentRole.D1, "plan"): (
        "incident-investigator-d1-orchestrator",
        "v3",
        "D1 incident scope and specialist-plan prompt.",
        "app.agents.d1_orchestrator.prompt",
        "SYSTEM_PROMPT",
    ),
    (AgentRole.D3, "investigate"): (
        "incident-investigator-d3-observability",
        "v2",
        "D3 bounded observability investigation prompt.",
        "app.agents.d3_observability.prompt",
        "SYSTEM_PROMPT",
    ),
    (AgentRole.D4, "investigate"): (
        "incident-investigator-d4-code-deploy",
        "v2",
        "D4 bounded code, deployment and configuration investigation prompt.",
        "app.agents.d4_code_deploy.prompt",
        "SYSTEM_PROMPT",
    ),
    (AgentRole.D5, "investigate"): (
        "incident-investigator-d5-data",
        "v2",
        "D5 read-contract-scoped data investigation prompt.",
        "app.agents.d5_data.prompt",
        "SYSTEM_PROMPT",
    ),
    (AgentRole.D6, "investigate"): (
        "incident-investigator-d6-ai-behavior",
        "v2",
        "D6 bounded AI runtime investigation prompt.",
        "app.agents.d6_ai_behavior.prompt",
        "SYSTEM_PROMPT",
    ),
    (AgentRole.D7, "review"): (
        "incident-investigator-d7-critic",
        "v2",
        "D7 evidence-claim review prompt.",
        "app.agents.d7_critic.prompt",
        "SYSTEM_PROMPT",
    ),
    (AgentRole.D7, "review_report"): (
        "incident-investigator-d7-report-review",
        "v3",
        "D7 exact-report delivery-gate prompt.",
        "app.agents.d7_critic.prompt",
        "REPORT_REVIEW_PROMPT",
    ),
    (AgentRole.D8, "write"): (
        "incident-investigator-d8-reporter",
        "v3",
        "D8 evidence-cited incident report prompt.",
        "app.agents.d8_reporter.prompt",
        "SYSTEM_PROMPT",
    ),
}


def prompt_spec(role: AgentRole, operation: str) -> PromptSpec:
    identifier, version, description, module_name, attribute = _PROMPT_DEFINITIONS[
        (role, operation)
    ]
    module = importlib.import_module(module_name)
    return PromptSpec(identifier, version, description, getattr(module, attribute))


def prompt_metadata(role: AgentRole, operation: str) -> dict[str, str]:
    spec = prompt_spec(role, operation)
    return {
        "prompt_identifier": spec.identifier,
        "prompt_version": spec.version,
        "prompt_sha256": spec.sha256,
    }


def push_all_prompts(client: Client) -> list[str]:
    """Synchronize exact code-owned system prompts as private LangSmith prompt versions."""

    commits = []
    for role, operation in _PROMPT_DEFINITIONS:
        spec = prompt_spec(role, operation)
        prompt = ChatPromptTemplate.from_messages([("system", spec.system_prompt)])
        try:
            commits.append(
                client.push_prompt(
                    spec.identifier,
                    object=prompt,
                    description=spec.description,
                    tags=["incident-investigator", "code-owned"],
                    commit_tags=[spec.version],
                    commit_description=f"Code prompt {spec.version}; sha256={spec.sha256}",
                )
            )
        except LangSmithConflictError as exc:
            # LangSmith may reject an idempotent repeat because the exact version tag already
            # belongs to the unchanged commit. That is equivalent to "Nothing to commit".
            if "Nothing to commit" not in str(exc) and "already exists on commit" not in str(exc):
                raise
            commits.append(f"{spec.identifier}:unchanged")
    return commits
