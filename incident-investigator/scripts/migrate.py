# ruff: noqa: E402
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow the documented `uv run python scripts/...` commands to import the
# application package when Python sets sys.path to the scripts directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.db.database import Database


async def main() -> None:
    settings = get_settings()
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is required to run migrations")
    database = Database(settings.database_url.get_secret_value())
    await database.connect()
    try:
        await database.apply_migration(
            PROJECT_ROOT / "supabase/migrations/202610200001_incident_investigator.sql"
        )
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())
