from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_TEXT_EXTENSIONS = {
    ".go",
    ".java",
    ".js",
    ".json",
    ".kt",
    ".md",
    ".py",
    ".rb",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
_SKIP_PARTS = {".git", ".gradle", "__pycache__", "dist", "node_modules", "target", "vendor"}
_TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_-]{3,}")


@dataclass(frozen=True)
class LocalCodeSearch:
    """Read-only, bounded retrieval from approved local source roots.

    This is a demo adapter for a production code-search/index gateway. The model controls only
    a text query; it cannot send a path, shell command, repository URL, revision or glob.
    """

    repository_root: Path
    deployment_fixture_root: Path

    def _roots(self) -> tuple[Path, ...]:
        return tuple(
            path for path in (self.repository_root, self.deployment_fixture_root) if path.exists()
        )

    @staticmethod
    def _tokens(query: str) -> list[str]:
        return list(dict.fromkeys(token.lower() for token in _TOKEN_PATTERN.findall(query)))[:8]

    async def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        if not self.repository_root.exists():
            raise RuntimeError(f"Approved repository is unavailable: {self.repository_root}")
        tokens = self._tokens(query)
        if not tokens:
            return []

        scored: list[tuple[int, Path, int, Path]] = []
        contents_by_path: dict[Path, list[str]] = {}
        for root in self._roots():
            for path in self._paths_for_root(root):
                try:
                    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
                except OSError:
                    continue
                contents_by_path[path] = lines
                path_score = sum(token in str(path.relative_to(root)).lower() for token in tokens)
                for line_number, line in enumerate(lines, start=1):
                    lowered = line.lower()
                    score = path_score + sum(token in lowered for token in tokens)
                    if score:
                        scored.append((score, path, line_number, root))

        scored.sort(key=lambda item: (-item[0], str(item[1]), item[2]))
        observed_at = datetime.now(UTC)
        results: list[dict[str, Any]] = []
        for score, path, line_number, root in scored[:limit]:
            relative = path.relative_to(root)
            source_group = "repository" if root == self.repository_root else "deployment-fixture"
            source_record_id = f"local-{source_group}:{relative}:{line_number}"
            lines = contents_by_path[path]
            if source_group == "deployment-fixture":
                snippet = "\n".join(lines[:80])
            else:
                start = max(0, line_number - 3)
                end = min(len(lines), line_number + 2)
                snippet = "\n".join(f"{index + 1}: {lines[index]}" for index in range(start, end))
            results.append(
                {
                    "source_record_id": source_record_id,
                    "observed_at": observed_at,
                    "summary": f"{source_group} match {relative}:{line_number}",
                    "content": (
                        f"source_group={source_group} path={relative} line={line_number}\n{snippet}"
                    ),
                    "coverage_note": (
                        "bounded read-only local source search across approved roots; "
                        f"matched {len(scored)} line(s), returned at most {limit}"
                    ),
                    "metadata": {
                        "source_group": source_group,
                        "path": str(relative),
                        "line": str(line_number),
                        "match_score": str(score),
                    },
                }
            )
        return results

    def _paths_for_root(self, root: Path) -> list[Path]:
        paths: list[Path] = []
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _TEXT_EXTENSIONS:
                continue
            if any(part in _SKIP_PARTS for part in path.parts):
                continue
            try:
                if path.stat().st_size <= 512_000:
                    paths.append(path)
            except OSError:
                continue
        return paths


@dataclass(frozen=True)
class TopologyIndex:
    """Small demo stand-in for a precomputed service/code/deployment topology index."""

    source: LocalCodeSearch

    async def resolve(self, query: str, limit: int = 8) -> dict[str, Any]:
        matches = await self.source.search(query, limit=limit)
        services: list[str] = []
        paths: list[str] = []
        for match in matches:
            path = match["metadata"]["path"]
            paths.append(path)
            pieces = Path(path).parts
            if len(pieces) >= 2 and pieces[0] == "src":
                services.append(pieces[1])
        return {
            "candidate_services": list(dict.fromkeys(services))[:6],
            "candidate_paths": list(dict.fromkeys(paths))[:limit],
            "coverage_note": (
                "candidate topology from the approved local demo index; it is a routing hint, "
                "not incident evidence or proof of deployment"
            ),
        }
