from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET = PROJECT_ROOT / "example-systems" / "opentelemetry-demo"
REFERENCE_URL = "https://github.com/open-telemetry/opentelemetry-demo.git"
REFERENCE_REVISION = "85c2cb2"


def main() -> None:
    """Fetch the immutable local D4 reference source without vendoring it in this repository."""

    if TARGET.exists():
        print(f"Reference repository already exists: {TARGET}")
        return
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", REFERENCE_URL, str(TARGET)],
        check=True,
    )
    subprocess.run(["git", "-C", str(TARGET), "checkout", REFERENCE_REVISION], check=True)
    print(f"Fetched {REFERENCE_URL} at {REFERENCE_REVISION}")


if __name__ == "__main__":
    main()
