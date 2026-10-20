# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langsmith import Client

from app.config import get_settings
from app.prompts import push_all_prompts


def main() -> None:
    settings = get_settings()
    if settings.langsmith_api_key is None:
        raise RuntimeError("LANGSMITH_API_KEY is required to publish code-owned prompts")
    client = Client(api_key=settings.langsmith_api_key.get_secret_value())
    commits = push_all_prompts(client)
    client.flush()
    print(f"Synchronized {len(commits)} private LangSmith prompt version(s).")


if __name__ == "__main__":
    main()
