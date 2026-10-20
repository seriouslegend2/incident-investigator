# Incident Investigator — real agent demo

This is a real OpenAI/LangGraph agent application, not a fixture that returns a stored answer.
Supabase contains seeded observability, data/history and AI-run records so the demo is repeatable.
D4 reads the locally cloned OpenTelemetry reference repository through a bounded path/line search
connector; it does not receive the repository in its prompt. Agents make live model calls and
case-scoped tool calls against these sources. No scenario stores a root-cause or final report.

For one D1 plan, the runnable LangGraph demo executes selected specialist tasks from a bounded
queue and calls D7 once only after that queue is complete. This prevents each result in a
fan-out from independently triggering a new D1 plan. A production worker pool may parallelize
independent tasks only with a durable batch join before D7.

## Structure

Each agent follows KookarCore’s folder convention:

```text
app/agents/
  d1_orchestrator/  __init__.py definition.py models.py prompt.py executor.py
  d3_observability/ __init__.py definition.py models.py prompt.py tools.py executor.py
  d4_code_deploy/   __init__.py definition.py models.py prompt.py tools.py executor.py
  d5_data/          __init__.py definition.py models.py prompt.py tools.py executor.py
  d6_ai_behavior/   __init__.py definition.py models.py prompt.py tools.py executor.py
  d7_critic/        __init__.py definition.py models.py prompt.py executor.py
  d8_reporter/      __init__.py definition.py models.py prompt.py executor.py
```

`app/agents/registry.py` discovers the seven `agent_definition` exports; D2 is deliberately
absent. D1 uses only the bounded topology tools. D3–D6 use small source-specific tool families
(3–4 calls per task); D4 reads only approved local source roots and D5 cannot construct a data
tool without D4's cited ReadContract. Every model invocation has a durable agent-run row and
LangSmith metadata containing case/task/agent-run IDs plus the exact prompt identifier, version
and SHA-256 hash. Every source tool call is case-scoped, parameterized, bounded and persisted as
evidence.

## Configure and run

1. Copy `.env.example` to `.env` and set `DATABASE_URL`, `OPENAI_API_KEY`, and the LangSmith
   variables. Use a separate demo Supabase/Postgres project; do not reuse an application
   service-role or production database.
2. Install and provision the demo schema/data:

   ```bash
   uv sync --all-groups
   uv run python scripts/fetch_reference_repo.py
   uv run python scripts/migrate.py
   uv run python scripts/seed_demo.py
   uv run python scripts/push_prompts.py
   ```

3. Run a genuine traced case:

   ```bash
   uv run python scripts/run_case.py email-confirmation-timeout \
     "Customer says their completed order did not receive a confirmation email."
   ```

   Or start the API:

   ```bash
   uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   curl http://127.0.0.1:8000/api/demo/scenarios
   curl -X POST http://127.0.0.1:8000/api/investigations \
     -H 'content-type: application/json' \
     -d '{"scenario_id":"email-confirmation-timeout","complaint":"Customer says their completed order did not receive a confirmation email."}'
   ```

With `LANGSMITH_TRACING=true`, one request-scoped root trace is created for the whole case. Its
D1/D3/D4/D5/D6/D7/D8/model/tool spans are nested beneath it and carry case/task/agent-run IDs and
prompt-version metadata. `scripts/push_prompts.py` publishes the exact code-owned system prompts
as private versioned LangSmith prompts. The API refuses to run agents if the OpenAI key or database
URL is absent; it never falls back to deterministic conclusions.

`run_case.py` prints one root LangSmith URL when tracing is on. To inspect the matching durable,
compact audit trail without dumping raw prompts or evidence, run:

```bash
uv run python scripts/inspect_case.py case_your_case_id
```

## Safety boundary

The demo intentionally has only seeded data. Tool arguments cannot choose a database host,
schema, tenant, arbitrary SQL, shell command or network URL. Moving to live sources requires the
private evidence-gateway adapter design in [the implementation plan](../research/implementation-plan.html),
with separate read-only identities and audited source catalogue entries.
