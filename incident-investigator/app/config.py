from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime-only configuration; secrets are never read from agent prompts or source data."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    langsmith_tracing: bool = False
    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "incident-investigator-demo"
    max_agent_rounds: int = Field(default=3, ge=1, le=5)
    max_critic_followups: int = Field(default=2, ge=0, le=3)
    max_tool_rows: int = Field(default=12, ge=1, le=25)
    reference_repository_path: Path = Field(
        default_factory=lambda: (
            Path(__file__).resolve().parents[1] / "example-systems/opentelemetry-demo"
        )
    )
    deployment_fixture_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "demo-fixtures/deployments"
    )

    @model_validator(mode="after")
    def validate_trace_pair(self) -> Settings:
        if self.langsmith_tracing and self.langsmith_api_key is None:
            raise ValueError("LANGSMITH_API_KEY is required when LANGSMITH_TRACING=true")
        return self

    @property
    def can_run_agents(self) -> bool:
        return self.openai_api_key is not None and self.database_url is not None

    def require_agent_runtime(self) -> None:
        missing = []
        if self.openai_api_key is None:
            missing.append("OPENAI_API_KEY")
        if self.database_url is None:
            missing.append("DATABASE_URL")
        if missing:
            raise RuntimeError(f"Live agent runtime is not configured: {', '.join(missing)}")

    def configure_langsmith_runtime(self) -> None:
        """Make Pydantic-loaded tracing settings visible to LangChain/LangGraph as well."""

        if not self.langsmith_tracing:
            return
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key.get_secret_value()
        os.environ["LANGSMITH_PROJECT"] = self.langsmith_project


@lru_cache
def get_settings() -> Settings:
    return Settings()
