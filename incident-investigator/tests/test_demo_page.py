from __future__ import annotations

import re
import subprocess

from app.demo_page import DEMO_PAGE


def test_live_demo_page_renders_only_real_api_data() -> None:
    assert "/api/investigations/start" in DEMO_PAGE
    assert "/timeline" in DEMO_PAGE
    assert "D8 final incident report" in DEMO_PAGE
    assert "Ranked hypotheses" in DEMO_PAGE


def test_live_demo_page_embedded_javascript_parses() -> None:
    script = re.search(r"<script>(.*?)</script>", DEMO_PAGE, re.DOTALL)
    assert script is not None
    result = subprocess.run(
        ["node", "--check", "-"],
        input=script.group(1),
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
