from __future__ import annotations

from pathlib import Path

import asyncpg


class Database:
    """Small asyncpg boundary. All source reads remain parameterized in repositories."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self._database_url,
                min_size=1,
                max_size=5,
                command_timeout=20,
            )

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Database is not connected")
        return self._pool

    async def apply_migration(self, migration_path: Path) -> None:
        sql = migration_path.read_text(encoding="utf-8")
        async with self.pool.acquire() as connection:
            await connection.execute(sql)
