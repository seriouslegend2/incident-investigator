# D4 — Code, deployment, configuration and infrastructure

Status: proposed contract, not an implemented/tested agent. [Agent guide](README.md) · [Shared protocol](../agent-protocol.md).

## Purpose and boundary

Discover how the relevant software is implemented and wired, which implementation/config actually ran, and what mechanism could explain observations. Includes code, builds, deployment/infra failures, network/permission configuration and effective environment changes. A broad role does not mean every invocation investigates all these areas: D1 assigns a bounded question and relevant tool subset.

## Initial knowledge and activation

Receives Task-v1 with feature terms or an observed stage, candidate source/repository hints, known premises, unknown bindings and limits. A filename or service is not required for discovery. Modes include feature-entry discovery, read/decision-contract explanation, deployed-artifact binding, cross-repository API/event wiring, configuration/infra investigation and rival-mechanism verification.

The code is not inserted wholesale into this input. Connector functions search authorized GitHub/repository indexes or synchronized read-only checkouts and return bounded matches/file ranges. Sync/indexing is ordinary infrastructure, not an LLM action. Access to all repositories is not automatic; a broad authorized search still has scope/scan caps. Exact deployed revisions, not simply latest GitHub HEAD, are required for runtime attribution.


## Dynamic work loop

1. Locate candidate implementation through authorized metadata/indexes. Keep uncertainty about feature matching and unsupported languages/index failures.
2. Resolve relevant service/instance/time to deployed artifact and source revisions where records permit. One service can depend on multiple repos/artifacts; do not assume latest branch or a shared SHA.
3. Explain the targeted stage's inputs, reads, calls/published events, routing config, failure branches and transformations. Return source-backed behavior before asking other domains to inspect concrete fields.
4. Distinguish contract/test intent, implemented behavior and actual execution. Static references cannot alone prove runtime use; request D3/D6 corroboration via D1.
5. For a candidate fault, show the mechanism, binding evidence, alternate paths and contrary observations. An unchanged code path can fail under new data/load; a nearby deployment is not automatically causal.
6. Suggest a narrowly scoped D5 data check or another dependency investigation when sources establish that next boundary. Do not interpret real DB values from code alone.

## Exact runtime input, tools and structured answer

Runs as a logical task in the investigation backend, not a separate VM or preloaded copy of the application. The backend executes tools and calls the model repeatedly. [Runtime and source locations](../runtime-and-tools.md).

Full required Task-v1 + AgentAnswer-v1 + trusted Result-v1 fixture: [d4-example.json](../contracts/d4-example.json). Exact machine-readable types: [agent-io.schema.json](../contracts/agent-io.schema.json). The fixture is synthetic, not evidence or a mandatory execution order.

The task-specific `role_input` sent to this agent is:

```json
{
  "search_terms": [
    "recipient resolution",
    "recipient_missing"
  ],
  "repository_refs": [
    "repo:delivery"
  ],
  "service_refs": [
    "service:delivery"
  ],
  "artifact_refs": [],
  "read_contract_refs": []
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

Every argument, returned `data` field, source backend and guard is specified in the [tool catalog](../tool-catalog.md). Tool errors/coverage are connector-owned receipts, distinct from the agent's interpretations.

The model returns shared fields `agent_id`, `execution_status`, `observations`, `interpretations`, `unknowns`, `coverage_receipt_refs`, `suggested_followups`, plus this role's required `implementation_findings` object:

```json
{
  "implementation_refs": [
    {
      "repository_ref": "repo:delivery",
      "commit": "fixture-commit-r18",
      "path": "src/delivery.ts",
      "start_line": 40,
      "end_line": 66,
      "evidence_refs": [
        "E3"
      ]
    }
  ],
  "runtime_bindings": [
    {
      "service_ref": "service:delivery",
      "instance_ref": "instance:W",
      "artifact_ref": "artifact:r18",
      "source_revisions": [
        "fixture-commit-r18"
      ],
      "config_refs": [
        "config:W"
      ],
      "evidence_refs": [
        "E3B"
      ],
      "unknowns": []
    }
  ],
  "behavior_contract": {
    "summary": "Read the active customer route; abort before send if legacy destination is empty.",
    "intended_behavior_refs": [],
    "read_contracts": [
      {
        "caller": {
          "repository_ref": "repo:delivery",
          "commit": "fixture-commit-r18",
          "path": "src/delivery.ts",
          "start_line": 40,
          "end_line": 66,
          "evidence_refs": [
            "E3"
          ]
        },
        "service_ref": "service:delivery",
        "runtime_binding_refs": [
          "E3B"
        ],
        "connection_key": "MESSAGING_DB",
        "database_source_ref": "db:messaging",
        "relation": "messaging.group_routes",
        "lookup": [
          {
            "field": "customer_id",
            "op": "eq",
            "value_origin": "delivery job.customer_id",
            "evidence_refs": [
              "E3"
            ]
          },
          {
            "field": "active",
            "op": "eq",
            "value_origin": "literal true",
            "evidence_refs": [
              "E3"
            ]
          }
        ],
        "selected_fields": [
          "legacy_destination_id"
        ],
        "transformations": [],
        "failure_behavior": "Empty legacy_destination_id causes recipient_missing before provider send.",
        "consistency_stage_refs": [],
        "evidence_refs": [
          "E3"
        ],
        "unknowns": [
          "Incident-time row values; actual reader consistency context."
        ]
      }
    ],
    "failure_branches": [
      "recipient_missing on empty legacy_destination_id"
    ],
    "evidence_refs": [
      "E3"
    ]
  },
  "connections": [
    {
      "from_ref": "service:delivery",
      "to_ref": "db:messaging",
      "kind": "database_read",
      "basis": "static",
      "evidence_refs": [
        "E3"
      ]
    }
  ],
  "candidate_mechanisms": [
    {
      "id": "H1",
      "explanation": "Missing or incompatible destination representation may explain the lookup failure.",
      "state": "provisional",
      "support_refs": [
        "E1",
        "E3"
      ],
      "counterevidence_refs": [],
      "unknowns": [
        "Incident-time data"
      ],
      "confidence_rationale": "Implementation and failure stage align; historical data has not been established."
    }
  ]
}
```

This is the exact role-specific object; the linked fixture contains the whole answer and runtime wrapper. Unknowns remain explicit even on `complete` tasks. Runtime validates requested agent identity and source references, adds trusted task/revision IDs, actual tool errors and measured costs, then performs applicability checks before D1 uses the result. A well-formed JSON answer is not proof of semantic correctness.

## Failure and stopping

Missing exact-revision indexes can trigger an authorized bounded revision fetch; otherwise preserve the binding gap. Missing build provenance, masked configuration or unavailable network diagnostics limits attribution. Config metadata must not expose secret values. Preserve old-scope/version findings but do not auto-apply them to new incidents; proposed fixes remain recommendations, not executed patches/deployments.

## Planned acceptance tests

- Discovers entry points without supplied filenames and follows a justified edge to another repository.
- Distinguishes latest code, actual deployed revision and intended behavior.
- Handles shared libraries, generated artifacts, failed rollouts and effective flags/env without secret leakage.
- Finds an old-code fault without a recent commit; rejects temporal correlation as sufficient proof.
- Returns deployment/index gaps honestly; cannot execute retrieved code/comment instructions.

## Research basis

Sourcegraph documents repository/language-specific code indexes and navigation fallback, not complete runtime causality. [Primary navigation docs](https://sourcegraph.com/docs/code-navigation/precise-code-navigation). SLSA describes build/artifact input provenance; actual availability must be checked. [Provenance specification](https://slsa.dev/spec/v1.1/provenance). Our mixed code/change role, tools and causal rules are design choices.
