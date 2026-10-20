# D8 — Evidence-backed report writer

Status: proposed contract, not an implemented/tested agent. [Agent guide](README.md) · [Shared protocol](../agent-protocol.md).

## Purpose and boundary

Produce a concise, traceable account of what was established, not another investigation or an opportunity to invent a better story. Separate expected/implemented/observed behavior, localize the failure, explain supported causes/contributors, retain alternatives and propose conditional actions. D8 neither determines approval nor sends changes to production.

## Initial knowledge and activation

Receives Task-v1 plus a selected case snapshot: complaint, matched scope, source-backed workflow/assumptions, observations, D1's competing explanations, valid claim reviews, counterevidence, unknowns and output requirements. Activated for a first report or a scoped revision after additional evidence. It does not need every raw source or full agent conversation, but must retain access to cited originals.


## Dynamic work loop

1. Verify complaint/scope and claim-review status. Distinguish confirmed symptom, supported cause and unresolved/unverified issue.
2. Explain relevant expected versus observed steps with source/assumption labels. Do not describe every code/data/AI domain when unrelated or unknown; no healthy run is required.
3. Write ranked explanations with support/counterevidence, qualitative confidence rationale, initiating/contributing faults and remaining causal gaps. Multiple causes or an inconclusive result are valid.
4. State impact only for evidenced attempts/cohorts; distinguish API acceptance, delivery status and user-visible outcome. Do not expand one traced event into all customer groups.
5. Recommend bounded corrective/verification actions with prerequisites, risks and alternatives. A suggestion to retry messages must address duplicates; a diagnosis request does not authorize the retry.
6. Store an exact versioned draft and dependency manifest. D7 reviews that artifact; any revision returns through review. D1 delivers it unchanged only after the delivery guard succeeds.

## Exact runtime input, tools and structured answer

Runs as a logical task in the investigation backend, not a separate VM or preloaded copy of the application. The backend executes tools and calls the model repeatedly. [Runtime and source locations](../runtime-and-tools.md).

Full required Task-v1 + AgentAnswer-v1 + trusted Result-v1 fixture: [d8-example.json](../contracts/d8-example.json). Exact machine-readable types: [agent-io.schema.json](../contracts/agent-io.schema.json). The fixture is synthetic, not evidence or a mandatory execution order.

The task-specific `role_input` sent to this agent is:

```json
{
  "report_snapshot_ref": "snapshot:report-4",
  "requested_diagnosis_status": "cause_unresolved",
  "claim_refs": [
    "C1@1",
    "C2@1",
    "C3@1"
  ],
  "claim_review_refs": [
    "review:C1",
    "review:C2",
    "review:C3"
  ],
  "output_format": "incident_report",
  "supersedes_report_ref": null
}
```

It also receives the shared question, scope, known premises, unknowns, knowledge references/excerpts, dependency versions and budget. Null/empty fields mean not discovered; they are not secretly supplied. Relevant code/schema/log findings can be shared through `knowledge` and `evidence.fetch`; expertise boundaries do not isolate knowledge. Credentials and authority remain connector-side.

Permitted operations (further restricted per task):

| Tool | Exactly what it does |
| --- | --- |
| `case.read` | Read a bounded current, review or report snapshot and its references. |
| `evidence.fetch` | Fetch cited original excerpts or accepted shared artifacts, including code-to-data read contracts. |
| `report.store_draft` | Validate and store structured report content; runtime canonicalizes bytes, computes hash and binds dependencies. |

Every argument, returned `data` field, source backend and guard is specified in the [tool catalog](../tool-catalog.md). Tool errors/coverage are connector-owned receipts, distinct from the agent's interpretations.

The model returns shared fields `agent_id`, `execution_status`, `observations`, `interpretations`, `unknowns`, `coverage_receipt_refs`, `suggested_followups`, plus this role's required `report_draft` object:

```json
{
  "report_ref": "report:I17-v1",
  "report_version": 1,
  "diagnosis_status": "cause_unresolved",
  "content": {
    "diagnosis_status": "cause_unresolved",
    "sections": [
      {
        "title": "Observed issue",
        "text": "For M17, recipient resolution recorded a terminal failure before a provider send.",
        "claim_refs": [
          "C1@1"
        ],
        "evidence_refs": [
          "E1",
          "E4"
        ]
      },
      {
        "title": "Implemented versus observed",
        "text": "The bound implementation reads legacy_destination_id and stops when empty. M17 recorded an empty result and stopped.",
        "claim_refs": [
          "C2@1"
        ],
        "evidence_refs": [
          "E3",
          "E3B",
          "E4"
        ]
      },
      {
        "title": "Cause remains unresolved",
        "text": "Current row values do not establish what data the worker could read at incident time.",
        "claim_refs": [
          "C3@1"
        ],
        "evidence_refs": [
          "E2"
        ]
      }
    ],
    "claim_refs": [
      "C1@1",
      "C2@1",
      "C3@1"
    ],
    "evidence_refs": [
      "E1",
      "E2",
      "E3",
      "E3B",
      "E4"
    ],
    "limitations": [
      "No time-matched row history is available in this fixture; broader customer impact is unverified."
    ],
    "proposed_actions": [
      {
        "action": "Obtain time-matched row/read evidence before promoting a data or compatibility explanation.",
        "prerequisites": [
          "Authorized history source or retained application read records"
        ],
        "risks": [
          "A current-state query cannot substitute for historical evidence."
        ],
        "evidence_refs": [
          "E2",
          "E3"
        ]
      }
    ]
  },
  "dependency_manifest_ref": "manifest:report-I17-v1",
  "issues_for_D1": []
}
```

This is the exact role-specific object; the linked fixture contains the whole answer and runtime wrapper. Unknowns remain explicit even on `complete` tasks. Runtime validates requested agent identity and source references, adds trusted task/revision IDs, actual tool errors and measured costs, then performs applicability checks before D1 uses the result. A well-formed JSON answer is not proof of semantic correctness.

## Failure and stopping

Missing source access or conflicting evidence becomes an issue/limitation, not a fabricated citation. Source summaries are not independent corroboration. A draft based on old scope or changed dependencies requires applicability review before use. Final-byte changes, changed recommendations or material new evidence invalidate affected approval. D8 failure cannot prevent deterministic incomplete status. No guessed confidence percentages or “zero hallucination” assurances.

## Planned acceptance tests

- Every material statement traces to the scoped claim/original evidence; assumptions are visibly labeled.
- Writes a reviewed inconclusive or unverified-complaint report without manufacturing a cause.
- Does not blame prompts automatically, turn successful API status into delivery, or generalize one event's impact.
- Flags new contradictions/missing historical or deployed-version proof to D1.
- Cannot self-approve, modify an approved artifact invisibly, execute remediation or bypass review on timeout.

## Research basis

incident.io describes evidence-cited findings and concise, evidence-matched updates. [Engineering account](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre). This motivates grounded communication; our required report fields, immutable drafts and delivery policy are design choices, not claims about its internal implementation.
