# Setup and traced demo

The runnable application is [`../incident-investigator/`](../incident-investigator/). It uses FastAPI, LangGraph, OpenAI, Supabase/Postgres, and LangSmith.

## Prerequisites

Create `incident-investigator/.env` from `.env.example`. Set a dedicated demo `DATABASE_URL`, `OPENAI_API_KEY`, and the LangSmith variables. Do not point the demo at a production database or use production service credentials.

## Provision the demo

```bash
cd incident-investigator
uv sync --all-groups
uv run python scripts/fetch_reference_repo.py
uv run python scripts/migrate.py
uv run python scripts/seed_demo.py
uv run python scripts/push_prompts.py
```

The reference repository is cloned at a pinned revision and is intentionally ignored by Git. D4 reads only bounded snippets from approved local roots; it never receives the repository in its model prompt.

## Run one real investigation

```bash
uv run python scripts/run_case.py email-confirmation-timeout \
  "Customer says their completed order did not receive a confirmation email."
```

With LangSmith tracing enabled, the script prints the LangGraph orchestration trace link. Every
invoked agent is also separately listed as a root trace named `agent/<role>/<operation>`, with
nested `tool/<role>/<tool>` spans for its bounded source reads. Filter the project by `case_id` to
see all roots for one case. Open one agent trace's **Inputs** to see its exact system prompt, scoped
input and allowed tools; open **Outputs** to see its structured result and handoff. D3/D4/D6 are
independent parallel agent traces. To inspect the durable case ledger without dumping raw data:

Each agent pulls the exact tagged prompt from LangSmith at runtime (for example,
`incident-investigator-d3-observability:v2`). The checked-in `prompt.py` source is a cached outage
fallback only, and the trace identifies it as `prompt_source: code-fallback` if used.

```bash
uv run python scripts/inspect_case.py case_your_case_id
```

For a video-friendly live view, start the API and open `http://127.0.0.1:8000/`:

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The page starts the real graph in the background, polls safe agent/tool receipts, and renders the final D8 response only when D7 has approved it.

## Run checks

```bash
uv run ruff format --check app scripts tests
uv run ruff check app scripts tests
uv run pytest -q
node ../research/contracts/check-doc-links.mjs
```

## Current safety boundaries

- D1 can only use topology/index tools; it cannot query raw logs, databases or source code.
- D3–D6 receive small role-specific tool families and call caps.
- D4 cannot run shell commands or choose an arbitrary local path/revision.
- D5 is constrained to a backend-controlled read-only data contract. It cannot send SQL, choose a host or write data.
- Supabase writes are investigator-owned audit records, not edits to the application under investigation.
