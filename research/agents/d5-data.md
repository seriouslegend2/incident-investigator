# D5 — Database, data correctness and read-path consistency

Status: proposed contract, not an implemented/tested agent. [Agent guide](README.md) · [Shared protocol](../agent-protocol.md).

## Purpose and boundary

Investigate actual scoped data, its read/transform path, historical values and database behavior. A healthy database can contain wrong data; a correct primary row can still be read incorrectly through a query, replica, cache or index. These layers are capabilities to discover, not components presumed to exist.

## Initial knowledge and activation

Receives Task-v1 with a discovered read/source reference or a discovery question, entity/run identifiers if available, time/version uncertainty, premises and limits. Modes include schema/read-path discovery, record correctness, incident-time history, cache/replica/index consistency where established, query semantics and DB performance/locking/connection diagnostics. If a requested field/source is not established, return `unknowns` and request discovery rather than invent it.

D5 does not have to guess tables from an incident sentence. The normal code-to-data task includes D4's ReadContract and cited lookup snippet: repository/commit, caller, connection identity, candidate relation, keys/predicates, selected fields, transformations and failure behavior. D5 fetches originals, resolves the environment-specific database and approved replica, and verifies actual schema before querying. With no established read path it can search source/schema metadata and report candidates; D1 asks D4 to establish actual application usage. Specialization does not prohibit D5 understanding relevant code.

Record-query tools execute on configured read replicas using connector-held least-privilege credentials, not the application's privileged key. No implicit primary fallback, updates, arbitrary SQL/RPC or active mutation tests. Replica freshness and missing historical state are explicit. Diagnostics unavailable on the replica need separately authorized monitoring metadata or remain gaps.


## Dynamic work loop

1. Establish actual source identity, namespace/tenant, entity keys, relevant schema and application read semantics. Ask D4/D6 via D1 if the caller's query/tool is unknown.
2. Read minimum necessary data/diagnostics, preserving actual query parameters, status and source evidence.
3. Separate current values, transaction/query snapshot, event/commit time and true historical/audit state. A stable current snapshot is not a time machine.
4. Compare what existed with what the application actually queried/read; a populated alternate field alone does not prove the running code used it.
5. Follow transformations/replicas/caches only when discovered or explicitly explored. Record consistency/freshness limits and competing explanations.
6. Return observations, current-versus-historical limits, candidate mechanisms and targeted follow-ups. Do not finalize an incident's cause from one row or blame DB health without mechanism.

## Exact runtime input, tools and structured answer

Runs as a logical task in the investigation backend, not a separate VM or preloaded copy of the application. The backend executes tools and calls the model repeatedly. [Runtime and source locations](../runtime-and-tools.md).

Full required Task-v1 + AgentAnswer-v1 + trusted Result-v1 fixture: [d5-example.json](../contracts/d5-example.json). Exact machine-readable types: [agent-io.schema.json](../contracts/agent-io.schema.json). The fixture is synthetic, not evidence or a mandatory execution order.

The task-specific `role_input` sent to this agent is:

```json
{
  "mode": "history",
  "source_refs": [
    "db:messaging-replica"
  ],
  "schema_refs": [],
  "read_contract_refs": [
    "RC1"
  ],
  "entity_keys": [
    {
      "field": "customer_id",
      "value": "G42",
      "evidence_refs": [
        "E1"
      ]
    }
  ]
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
| `data.describe_source` | Resolve database identity, replica relationship, query/history support and freshness. |
| `data.inspect_schema` | Search permitted relation/column metadata or describe a discovered relation. |
| `data.read_bounded` | Execute a validated parameterized read or an approved read template. |
| `data.history` | Read retained changes/historical values for an established data scope. |
| `data.lineage` | Find established views, transformations, replica/cache/index relationships. |
| `data.diagnostics` | Read available query-plan metadata/statistics, locks, connection or replication health. |
| `data.read_cache_index` | Read narrowly identified cache entries or indexed documents and version/TTL metadata. |

Every argument, returned `data` field, source backend and guard is specified in the [tool catalog](../tool-catalog.md). Tool errors/coverage are connector-owned receipts, distinct from the agent's interpretations.

The model returns shared fields `agent_id`, `execution_status`, `observations`, `interpretations`, `unknowns`, `coverage_receipt_refs`, `suggested_followups`, plus this role's required `data_findings` object:

```json
{
  "read_scope": {
    "source_ref": "db:messaging-replica",
    "schema_refs": [
      "schema:routes-v1"
    ],
    "read_contract_refs": [
      "RC1"
    ],
    "entity_keys": [
      {
        "field": "customer_id",
        "value": "G42",
        "evidence_refs": [
          "E1"
        ]
      }
    ],
    "query_receipt_refs": [
      "call:D5-read"
    ]
  },
  "values_or_diagnostics": [
    {
      "description": "Current row has destination_id=chat-7 and legacy_destination_id=null.",
      "evidence_refs": [
        "E2"
      ],
      "redacted": false
    }
  ],
  "temporal_basis": {
    "current_state_only": true,
    "historical_state_established": false,
    "history_interval": null,
    "freshness_receipt_refs": [
      "call:D5-read"
    ],
    "limitations": [
      "No configured audit source for the requested interval; replica replay watermark unknown."
    ]
  },
  "consistency_path": [
    {
      "source_ref": "db:messaging-replica",
      "kind": "replica",
      "evidence_refs": [
        "E2"
      ],
      "unknowns": [
        "Freshness and actual application read snapshot at incident time."
      ]
    }
  ],
  "application_read_match": {
    "status": "partial",
    "explanation": "Current schema supports the code lookup; incident-time visibility is unverified.",
    "evidence_refs": [
      "E2",
      "E3"
    ],
    "unknowns": [
      "Values visible to the worker at 10:32."
    ]
  }
}
```

This is the exact role-specific object; the linked fixture contains the whole answer and runtime wrapper. Unknowns remain explicit even on `complete` tasks. Runtime validates requested agent identity and source references, adds trusted task/revision IDs, actual tool errors and measured costs, then performs applicability checks before D1 uses the result. A well-formed JSON answer is not proof of semantic correctness.

## Failure and stopping

No matches under one query do not establish global record absence. Partial pages, denied access, replica lag or timeout must not become “data missing.” Return useful observations with coverage and costs; retry only retriable reads within shared limits. Late group-A results cannot explain group B. Changed historical/source evidence can invalidate dependent causal claims and report approval. Flag potential mutation or unsafe query cost rather than execute it.

## Planned acceptance tests

- Missing record versus wrong tenant/filter versus stale replica/cache are distinguished when evidence permits.
- Current-state query success cannot prove incident-time values; missing audit history yields uncertainty.
- Source correctness is not confused with actual application read correctness.
- Database locks/connections/performance and data integrity faults are both supported capabilities.
- Query timeouts/partial pages, PII restrictions and stale-scope results cannot silently become negative findings.

## Research basis

PostgreSQL documents that statement/transaction snapshots and isolation behavior differ; successive reads can observe different committed states. [Primary isolation documentation](https://www.postgresql.org/docs/current/transaction-iso.html). This motivates recording consistency context, not requiring PostgreSQL or long-running transactions in production. Historical availability and the proposed agent's conclusions must be established from actual sources.
