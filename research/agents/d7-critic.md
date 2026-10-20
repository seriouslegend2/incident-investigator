# D7 — Independent premise, causal and report critic

Status: proposed contract, not an implemented/tested agent. [Agent guide](README.md) · [Shared protocol](../agent-protocol.md).

## Purpose and boundary

Challenge whether original evidence supports a premise, mechanism or exact report. Detect unsupported components/fields, selective evidence, wrong scope/version, omitted prerequisites, contradictory cohorts and overconfident actions. D7 is not a proof oracle, the primary investigator approving its own explanation, a second orchestrator or a permanent monitor for every specialist call.

## Initial knowledge and activation

Receives Task-v1 plus an explicit review target, claim/report versions, scope, dependency manifest, known supporting/contradicting sources, query coverage and unresolved frontier. Use fresh review context rather than the investigator's accumulated narrative; shared-model bias is still possible.

Review is policy-required at first cross-domain use of a new architecture/read-contract premise, flagged contradictions/prerequisite gaps, causal promotion and final delivery. Related premises can be batched. This gate is not solely D1 deciding when to request criticism.


## Dynamic work loop

1. Check target identity/scope/dependency versions and whether the review packet is complete enough to assess. A real citation ID can refer to the wrong function, tenant or time.
2. Inspect originals underlying material premises. Separate implementation existence, deployed activation, observed execution, intended behavior and causal interpretation.
3. Ask what could contradict the leading explanation. Look for alternative mechanisms and missing causal links without requiring a fixed number of hypotheses.
4. Verify prerequisites for the claim: incident-time data, correct caller/query, actual rendered AI context, effective deployment/config and evidence coverage as relevant—not every domain on every case.
5. Return a scoped verdict and concrete follow-up. A code fact can be accepted while incident attribution stays insufficient.
6. For final review, audit the exact report bytes/hash, scope, cause ranking, facts/assumptions, limitations, confidence and proposed actions. Approve only that artifact/manifest; runtime still checks freshness at delivery.

## Exact runtime input, tools and structured answer

Runs as a logical task in the investigation backend, not a separate VM or preloaded copy of the application. The backend executes tools and calls the model repeatedly. [Runtime and source locations](../runtime-and-tools.md).

Full required Task-v1 + AgentAnswer-v1 + trusted Result-v1 fixture: [d7-example.json](../contracts/d7-example.json). Exact machine-readable types: [agent-io.schema.json](../contracts/agent-io.schema.json). The fixture is synthetic, not evidence or a mandatory execution order.

The task-specific `role_input` sent to this agent is:

```json
{
  "target": {
    "kind": "claims",
    "claim_refs": [
      "C2@1"
    ],
    "report_ref": null,
    "report_hash": null,
    "manifest_ref": "manifest:C2@1",
    "scope_revision": 2
  },
  "review_snapshot_ref": "snapshot:review-4",
  "supporting_refs": [
    "E1",
    "E3",
    "E4"
  ],
  "contradicting_refs": [],
  "unresolved_questions": [
    "Incident-time row values"
  ]
}
```

It also receives the shared question, scope, known premises, unknowns, knowledge references/excerpts, dependency versions and budget. Null/empty fields mean not discovered; they are not secretly supplied. Relevant code/schema/log findings can be shared through `knowledge` and `evidence.fetch`; expertise boundaries do not isolate knowledge. Credentials and authority remain connector-side.

Permitted operations (further restricted per task):

| Tool | Exactly what it does |
| --- | --- |
| `catalog.search` | Find candidate sources/services/repos by feature terms; does not establish the failing component. |
| `catalog.describe` | Describe one discovered source, capabilities, relationships and freshness. |
| `history.search` | Retrieve useful precedent or intended-behavior documents. |
| `case.read` | Read a bounded current, review or report snapshot and its references. |
| `evidence.fetch` | Fetch cited original excerpts or accepted shared artifacts, including code-to-data read contracts. |
| `telemetry.describe_sources` | Inspect queryable fields, retention, sampling and supported correlation/status operations. |
| `telemetry.aggregate` | Run bounded counts/rates/distributions to narrow time, service or cohort. |
| `telemetry.query_events` | Fetch relevant original log/event records using validated terms, IDs and filters. |
| `telemetry.fetch_trace` | Read a specific trace and bounded span summaries/links. |
| `telemetry.correlate_messages` | Find records joined through discovered request/job/message/run keys. |
| `telemetry.read_status` | Read a discovered queue backlog, worker state or message delivery receipt. |
| `code.search` | Locate candidate paths, text matches or symbols across authorized repositories. |
| `code.read_at_revision` | Read an exact versioned file range; no execution of its code. |
| `code.references` | Find definitions, callers or references to a discovered symbol. |
| `code.diff` | Compare two discovered immutable source revisions. |
| `build.provenance` | Resolve a built artifact to recorded source inputs and build identity. |
| `deploy.history` | Read releases, failed rollouts and placement changes in a bounded interval. |
| `deploy.instance_binding` | Bind the affected instance/attempt time to artifact/config where recorded. |
| `config.effective` | Inspect effective nonsecret settings, connection identities and secret-version metadata. |
| `config.history` | Read recorded setting changes and effective intervals. |
| `infra.inspect` | Inspect a discovered infrastructure resource or policy for a bounded question. |
| `data.describe_source` | Resolve database identity, replica relationship, query/history support and freshness. |
| `data.inspect_schema` | Search permitted relation/column metadata or describe a discovered relation. |
| `data.read_bounded` | Execute a validated parameterized read or an approved read template. |
| `data.history` | Read retained changes/historical values for an established data scope. |
| `data.lineage` | Find established views, transformations, replica/cache/index relationships. |
| `data.diagnostics` | Read available query-plan metadata/statistics, locks, connection or replication health. |
| `data.read_cache_index` | Read narrowly identified cache entries or indexed documents and version/TTL metadata. |
| `ai.list_workflows` | Discover candidate application workflows by feature terms. |
| `ai.list_runs` | Find runs matching discovered scope, including successful-status quality failures. |
| `ai.fetch_run` | Inspect a run tree, observed stages and retained input/output references. |
| `ai.fetch_observation` | Read selected bounded step input/output/error content. |
| `ai.rendered_prompt` | Read instructions/context actually sent for the selected generation. |
| `ai.prompt_version` | Read a specific prompt version for comparison with actual generation inputs. |
| `ai.retrieval_trace` | Read actual retrieval query/filter/result IDs, scores and available source snippets. |
| `ai.tool_trace` | Read tool definition version, arguments, outcome and returned evidence content. |
| `ai.state_handoffs` | Read recorded routing and before/after state across actual agent steps. |
| `ai.model_metadata` | Read actual recorded provider/model/settings/finish metadata. |

Every argument, returned `data` field, source backend and guard is specified in the [tool catalog](../tool-catalog.md). Tool errors/coverage are connector-owned receipts, distinct from the agent's interpretations.

The model returns shared fields `agent_id`, `execution_status`, `observations`, `interpretations`, `unknowns`, `coverage_receipt_refs`, `suggested_followups`, plus this role's required `review` object:

```json
{
  "target": {
    "kind": "claims",
    "claim_refs": [
      "C2@1"
    ],
    "report_ref": null,
    "report_hash": null,
    "manifest_ref": "manifest:C2@1",
    "scope_revision": 2
  },
  "verdict": "insufficient",
  "accepted_scope": [
    "The inspected deployed lookup failed for M17."
  ],
  "objections": [
    {
      "text": "Current E2 values cannot establish incident-time data or prove a compatibility cause.",
      "affected_refs": [
        "C2@1",
        "H1"
      ],
      "evidence_refs": [
        "E2",
        "E3"
      ]
    }
  ],
  "required_followups": [
    {
      "agent_id": "D5",
      "question": "Establish incident-time values for the discovered lookup scope, or retain the gap.",
      "premise_refs": [
        "E1",
        "E3",
        "RC1"
      ],
      "unknowns": [
        "Historical row values"
      ],
      "expected_information": "Time-matched fields and source-history coverage."
    }
  ],
  "limitations": [
    "Incident-time row history is unavailable so far."
  ]
}
```

This is the exact role-specific object; the linked fixture contains the whole answer and runtime wrapper. Unknowns remain explicit even on `complete` tasks. Runtime validates requested agent identity and source references, adds trusted task/revision IDs, actual tool errors and measured costs, then performs applicability checks before D1 uses the result. A well-formed JSON answer is not proof of semantic correctness.

## Failure, invalidation and stopping

Malformed verdict, model timeout, denied originals or budget exhaustion cannot be treated as acceptance. Runtime can return `investigation_incomplete` without D7/D8 text generation. Material changes to reviewed premises, scope, recommendations or exact artifact invalidate affected approval; unrelated case updates need not invalidate everything. A late contradiction before delivery blocks stale approval; a contradiction after delivery needs a superseding record. Reuse only matching valid reviews, not reviewer agreement from another incident/cohort.

## Planned acceptance tests

- Rejects invented premises, real-but-irrelevant citations, unsupported deployment attribution and current-as-historical claims.
- Requests a rival source/cohort beyond D1's first branch; can accept a justified inconclusive report.
- Cannot approve modified report bytes or stale dependencies; appropriately reuses unchanged scoped reviews.
- Timeout/partial/denied/malformed review cannot bypass delivery guards.
- Measure false approvals, missed omissions, unnecessary rejections and review cost; do not assume fresh context ensures correctness.

## Research basis

Resolve documents structurally independent verification; incident.io describes adversarial hypothesis checks and findings that can be overturned. [Resolve](https://resolve.ai/blog/Failures-That-Led-to-2x-Agent-Accuracy-Improvement) · [incident.io](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre). Our exact verdict, mandatory-gate and approval-binding protocol is a proposal, not a verified feature of those systems.
