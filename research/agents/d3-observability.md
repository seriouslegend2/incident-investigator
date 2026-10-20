# D3 — Observability and observed execution

Status: proposed contract, not an implemented/tested agent. [Agent guide](README.md) · [Shared protocol](../agent-protocol.md).

## Purpose and boundary

Establish what execution/outcome evidence shows: candidate symptoms, affected cohorts, onset, boundaries reached and missing coverage. D3 investigates telemetry; it does not assume a known route, equate errors with causes or treat absence of spans as nonexecution.

## Initial knowledge and activation

Receives a shared Task with complaint/known observations, candidate scope if discovered, source directory hints, unknowns and budget. Discovery may begin with only feature terms; it must return ambiguity rather than select an arbitrary error. Activation modes include candidate discovery, bounded actual-path tracing, cohort/time comparison, provider outcome verification and contradictory-evidence checks. D3 is not mandatory first for every complaint.


## Dynamic work loop

1. Identify available relevant sources; record initial time/service assumptions and actual searched scope.
2. Use outcome/metric aggregates to narrow candidates where available, then inspect originals and counterexamples. Rare initiating events must not disappear behind frequent downstream errors.
3. Correlate request/job/message/run identifiers, producer/consumer links, environment/tenant and event/ingestion timing. Timestamp proximity alone is not a unique join.
4. Trace only justified boundaries. An explicit terminal outcome plus known implementation may support a skipped downstream call; missing instrumentation alone does not.
5. Compare healthy/affected cohorts when useful, noting differing payloads, time, load and versions. Separate provider acceptance, delivered status and customer visibility.
6. Return observations, limitations and focused follow-ups. Request D4's implementation or D6's AI semantics through D1 when telemetry cannot explain a stage.

## Exact runtime input, tools and structured answer

Runs as a logical task in the investigation backend, not a separate VM or preloaded copy of the application. The backend executes tools and calls the model repeatedly. [Runtime and source locations](../runtime-and-tools.md).

Full required Task-v1 + AgentAnswer-v1 + trusted Result-v1 fixture: [d3-example.json](../contracts/d3-example.json). Exact machine-readable types: [agent-io.schema.json](../contracts/agent-io.schema.json). The fixture is synthetic, not evidence or a mandatory execution order.

The task-specific `role_input` sent to this agent is:

```json
{
  "search_terms": [
    "customer group",
    "delivery"
  ],
  "source_refs": [
    "logs:delivery-prod"
  ],
  "correlation_keys": [],
  "implementation_contract_refs": []
}
```

It also receives the shared question, scope, known premises, unknowns, knowledge references/excerpts, dependency versions and budget. Null/empty fields mean not discovered; they are not secretly supplied. Relevant code/schema/log findings can be shared through `knowledge` and `evidence.fetch`; expertise boundaries do not isolate knowledge. Credentials and authority remain connector-side.

Permitted operations (further restricted per task):

| Tool | Exactly what it does |
| --- | --- |
| `catalog.search` | Find candidate sources/services/repos by feature terms; does not establish the failing component. |
| `catalog.describe` | Describe one discovered source, capabilities, relationships and freshness. |
| `case.read` | Read a bounded current, review or report snapshot and its references. |
| `evidence.fetch` | Fetch cited original excerpts or accepted shared artifacts, including code-to-data read contracts. |
| `telemetry.describe_sources` | Inspect queryable fields, retention, sampling and supported correlation/status operations. |
| `telemetry.aggregate` | Run bounded counts/rates/distributions to narrow time, service or cohort. |
| `telemetry.query_events` | Fetch relevant original log/event records using validated terms, IDs and filters. |
| `telemetry.fetch_trace` | Read a specific trace and bounded span summaries/links. |
| `telemetry.correlate_messages` | Find records joined through discovered request/job/message/run keys. |
| `telemetry.read_status` | Read a discovered queue backlog, worker state or message delivery receipt. |

Every argument, returned `data` field, source backend and guard is specified in the [tool catalog](../tool-catalog.md). Tool errors/coverage are connector-owned receipts, distinct from the agent's interpretations.

The model returns shared fields `agent_id`, `execution_status`, `observations`, `interpretations`, `unknowns`, `coverage_receipt_refs`, `suggested_followups`, plus this role's required `observed_execution` object:

```json
{
  "candidate_attempts": [
    {
      "entity_ref": "attempt:M17",
      "label": "Candidate group delivery",
      "match_reason": "Recorded delivery for the matched customer/time.",
      "evidence_refs": [
        "E1"
      ],
      "ambiguity": []
    }
  ],
  "boundaries": [
    {
      "stage": "recipient_resolution",
      "state": "explicit_failure",
      "correlation_basis": "Same discovered message/job identifier",
      "evidence_refs": [
        "E1"
      ]
    }
  ],
  "cohort_comparisons": [],
  "timeline": [
    {
      "event_time": "2026-10-20T10:32:00Z",
      "ingestion_time": null,
      "description": "Terminal recipient_missing",
      "evidence_refs": [
        "E1"
      ],
      "ordering_limits": "No full upstream trace established."
    }
  ],
  "outcome_semantics": [
    "This establishes a local failure, not its underlying cause."
  ]
}
```

This is the exact role-specific object; the linked fixture contains the whole answer and runtime wrapper. Unknowns remain explicit even on `complete` tasks. Runtime validates requested agent identity and source references, adds trusted task/revision IDs, actual tool errors and measured costs, then performs applicability checks before D1 uses the result. A well-formed JSON answer is not proof of semantic correctness.

## Failure and stopping

Return query-level timeout/denied/partial/empty distinctions and preserved useful records. Missing IDs may leave multiple possible joins; do not invent a trace. Retry transient faults within budget, then suggest another source or return gaps. Old-scope results and late events follow the shared applicability/invalidation rules. Do not claim provider health or estate-wide absence from one attempted path.

## Planned acceptance tests

- Async producer/consumer evidence uses links or message IDs rather than requiring a single trace.
- Sampled/missing/truncated telemetry cannot become proof that a step never happened.
- A rare initiating event survives an error storm; unrelated alarming logs do not automatically win.
- A provider accepted request is not reported as customer-visible delivery.
- Incorrect tenant/time joins, stale-scope results and repeated identical queries are detected or reported uncertain.

## Research basis

OpenTelemetry describes messaging context and producer/consumer relationships; its cited conventions are marked Development, so adapters must record versions. [Primary conventions](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/). Twilio documents outbound status transitions; those meanings are provider/channel-specific. [Status guide](https://www.twilio.com/docs/messaging/guides/track-outbound-message-status). Our agent contract and evidence judgments are proposed, not supplied by these standards.
