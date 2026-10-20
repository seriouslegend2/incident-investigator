from __future__ import annotations

import pytest
from langsmith.utils import LangSmithConflictError

from app.prompts import push_all_prompts


class _FakeClient:
    def push_prompt(self, name: str, **_: object) -> str:
        if name == "incident-investigator-d1-orchestrator":
            raise LangSmithConflictError("Tag v3 already exists on commit")
        return "new-commit"


def test_prompt_push_accepts_an_idempotent_existing_tag() -> None:
    commits = push_all_prompts(_FakeClient())  # type: ignore[arg-type]
    assert commits[0] == "incident-investigator-d1-orchestrator:unchanged"
    assert "new-commit" in commits


def test_prompt_push_keeps_real_conflicts_visible() -> None:
    class RejectingClient:
        def push_prompt(self, _: str, **__: object) -> str:
            raise LangSmithConflictError("permission denied")

    with pytest.raises(LangSmithConflictError, match="permission denied"):
        push_all_prompts(RejectingClient())  # type: ignore[arg-type]
