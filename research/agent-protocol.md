# Shared agent protocol and lifecycle rules

Status: proposed implementation contract, researched and reviewed on 20 October 2026. No runtime, model prompts, source integrations or behavioral tests are implemented by these documents. The active agents are D1, D3, D4, D5, D6, D7 and D8; D2 is removed. Start with the [agent guide](agents/README.md).

For physical deployment, the LLM/tool execution loop, credentials and where code/replicas/logs live, read [how the agents actually run](runtime-and-tools.md). The [tool catalog](tool-catalog.md) and [JSON schemas/examples](contracts/README.md) are the exact interface reference. Earlier conceptual payloads in historical architecture discussions are not additional APIs.

## 1. Stable roles, dynamic assignments

A role defines expertise and permitted capabilities, not a fixed task or mandatory execution order. Every invocation receives a bounded question, available knowledge, unknowns, output requirements and limits. Discovery tasks may lack service/time/version identifiers; they must record search assumptions, not invent those identifiers. Specialists reason locally and suggest follow-ups. Only D1 allocates cross-agent work; D7 can require missing evidence or reject a conclusion, but does not become a second orchestrator.

Production tools are read-only and tenant-scoped. Writing the investigator's own case records, task events and report drafts is allowed; that does not authorize production DB writes, message sends, deployments or arbitrary shell execution. Tool names in these contracts are proposed adapter interfaces, not installed integrations.

## 2. D1's bootstrap is explicit

At start D1 receives `report_text`, the configured role/tool registry, a trusted authorization context, source-directory access, an empty case/knowledge state and configured limits. It does not receive the correct service, incident time, workflow or cause.

D1 can use navigation tools: `catalog.search`, `catalog.describe`, `history.search`, `case.read`, targeted `evidence.fetch`, `delegate_task` and `request_clarification`. Tools enforce authorization outside model-controlled arguments. The directory contains searchable metadata, not guaranteed runtime truth. If it is missing/stale, perform bounded indexed discovery through an appropriate specialist or clarify scope; no unlimited organization-wide raw scan.

The four domain roles have deeper source adapters. Capabilities can overlap where justified; the role names are expertise boundaries, not isolated knowledge. D5 receives D4's discovered code-to-data ReadContract, cited code excerpts and unresolved bindings; it can fetch their originals. D4 can inspect relevant schema metadata. D5 can begin with source/schema discovery and request D4's verification when application usage is unknown. D7 has authorized original-evidence fetch and bounded verification queries so it is not restricted to D1's selected prose. D8 reads the selected case snapshot and cited originals, not unrestricted exploratory production searches.

## 3. Shared task envelope

Each Task contains these fields; example values are invented fixtures, not hidden input hints or tuned budgets. All object keys are required in the strict schema; unknown nullable values use null, collections use empty arrays. The model receives role instructions and permitted tool schemas separately. Credentials, trusted caller policy and executable tool code are not model inputs.

```json
{
  "protocol_version": "1",
  "case_id": "I17",
  "task_id": "T3",
  "attempt_id": "T3-A1",
  "agent_id": "D4",
  "case_revision": 4,
  "scope_revision": 2,
  "inquiry_kind": "discovery",
  "question": "Explain recipient resolution in the worker identified by E1.",
  "known_premises": [{"claim_ref": "C1@1", "evidence_refs": ["E1"]}],
  "exploratory_assumptions": [],
  "unknowns": ["lookup inputs", "read source", "failure branches", "deployed implementation"],
  "why_now": "E1 locates a recipient-resolution failure but does not explain its implementation.",
  "expected_information": "Source-backed read/decision behavior and version-binding gaps.",
  "scope": {"entity_refs": ["worker-W"], "feature_terms": ["recipient resolution"], "environment": null, "time_range": null, "repository_refs": []},
  "dependency_versions": [{"ref": "C1", "version": "1"}],
  "prerequisite_task_refs": ["T1"],
  "knowledge": {"brief": "E1 localizes a stage; its implementation is unknown.", "artifact_refs": [], "excerpts": [], "read_contract_refs": []},
  "budget": {"tool_calls_max": 6, "wall_ms_max": 30000, "model_tokens_max": 10000, "output_tokens_max": 2000},
  "role_input": {"search_terms": ["recipient resolution"], "repository_refs": [], "service_refs": ["worker-W"], "artifact_refs": [], "read_contract_refs": []},
  "output_contract": "AgentAnswer-v1"
}
```

`case_revision` identifies the planning snapshot; it changes on accepted case updates. `scope_revision` changes when the investigated entity/cohort/environment/time interpretation changes materially. `dependency_versions` identifies the particular claims/assumptions the task relies on. Artifact/source versions and actual searched time ranges belong in the source/coverage records. These are different concepts; a DB query snapshot is not an incident-time historical snapshot.

Authorization is attached in a trusted context, not granted by model-written `scope`. `inquiry_kind` is `discovery`, `hypothesis_test`, `verification`, `report_draft` or `report_review`. Unknowns may be empty, but every specific premise needs a basis or explicit exploratory label. Search terms may be tentative; invented resource IDs cannot be treated as discovered targets.

## 4. Model answer versus trusted result envelope

The runner repeatedly calls the LLM, executes validated requested tools and returns their bounded receipts. The model's final structured object is `AgentAnswer-v1`; it does not mint source evidence, runtime identity, hashes or measured costs:

| Field | Required meaning |
| --- | --- |
| `agent_id` | Must equal the role requested by the runtime; not permission to switch roles. |
| `execution_status` | `complete`, `partial`, `failed` or `cancelled`; complete means the assigned query/task finished, not that a cause was proved. |
| `observations` | Scoped source-backed observations, each with evidence references; interpretations stay separate. |
| `interpretations` | Provisional mechanisms/hypotheses with supporting/contradicting observations and unknowns. |
| `unknowns` | Explicit unanswered questions/missing prerequisites; these do not disappear when a query completes. |
| `coverage_receipt_refs` | Actual tool-receipt references carrying source scope, snapshots, sampling/retention/index freshness, pagination and limitations. The model cannot replace connector coverage with a claim of completeness. |
| `suggested_followups` | Question, proposed role, premise refs, missing prerequisite and expected information; suggestions are not automatically dispatched. |
| Role-specific extension | Defined in the individual agent contract below this shared envelope. |

Runtime constructs `Result-v1`: `protocol_version`, `result_id`, `case_id`, `task_id`, `attempt_id`, `agent_id`, `case_revision`, `scope_revision`, `dependency_versions`, `answer_state`, the validated `answer`, `tool_receipt_refs`, actual `errors`, and measured `cost` (elapsed/tool/model calls, nullable token and backend scan counts). `answer_state=valid` requires an answer; `unavailable`, `invalid` or `cancelled` uses `answer=null`. It validates identities/references before applicability checks. Exhausted model/schema-repair attempts preserve actual receipts and errors; no fabricated model answer or review acceptance is required for deterministic incomplete delivery.

Adapters register original evidence independently of agent prose. Observation/interpretation IDs inside a model answer are task-local labels; runtime assigns registered versioned claim/artifact IDs. Returned citations are checked against the source store and authorization. A real source ID can still be irrelevant; structural validation does not establish semantic support.

`delegate_task` is an idempotent D1-only control tool: validates a proposal, clamps/reserves budget and schedules once. Runtime fills task/attempt IDs and revisions. D1's `lead_decision.dispatched_task_refs` records those already-created tasks; its final answer must not enqueue them a second time. Specialists and D7 only suggest cross-agent follow-ups. Read-only production tools do not prevent investigator-owned task/artifact writes.

`report.store_draft` validates D8's structured content and freezes the artifact, hash and dependency manifest. D8 echoes returned identities; it cannot self-approve or invent a successful store. D7 receives that exact artifact and target manifest for report review. See [schemas and runtime-only checks](contracts/README.md).

## 5. Rule A: late parallel results do not blindly update current state

1. Receive an event identified by `case_id`, `task_id`, `attempt_id` and a unique result ID. Deduplicate ingestion; repeated delivery does not count as independent evidence or execute side effects twice.
2. Preserve authorized source evidence and the original result with its scope/dependency metadata. Do not overwrite current claims directly from a worker response.
3. Compare the task's scope/dependency versions with current state. A changed global case revision alone does not invalidate an independent result.
4. If the same question still applies and its dependencies/source bindings remain valid, atomically apply the result against current versions. If relevant scope/dependencies changed, mark `needs_revalidation`. D1 assesses applicability; required new premises still go through D7. Old-scope observations can remain useful history/counterevidence, but cannot silently become facts about the new scope.
5. Unauthorized/malformed results are rejected; obsolete results can be archived. Acceptance states are `applied`, `needs_revalidation`, `archived` or `rejected`, assigned by case-ingestion policy, not by the producing agent.

Example: D5 checks group A under scope revision 2. D1 changes the investigation to group B at revision 3. A's result arrives late: retain it as A-scoped history; do not use it to explain B. A separate result about unchanged worker code may still be reusable after applicability checks.

Use a transactional/version-checked state update and an append-only event/audit history; no particular database is selected. Cancellation is best-effort: even a cancelled task may return late. Shared limits still charge work already spent. Agents propose records; they cannot rewrite historical evidence, their own acceptance status or review approval.

## 6. Rule B: review approval is version-bound and revocable

A claim review targets claim revisions, scope and a dependency manifest of source references/versions, related claims, coverage and relevant missing/contradicting evidence. D7 verdicts are `accept`, `revise`, `insufficient` or `failed`. Acceptance is scoped support, not proof of universal truth.

A final report review also binds the exact report bytes/hash and report version, diagnosis status, scope revision and dependency manifest. Report hashes bind artifacts; they do not prove claims are true. Normal formatting/encoding is finalized before review. D1 may add transport metadata outside the artifact but may not paraphrase the approved report.

Materially changed scope, changed supporting premises, new relevant contradictory evidence, withdrawn support, changed limitations/actions or changed report bytes invalidate affected approval. Unrelated evidence or an independent task event need not trigger a complete re-review. Track dependencies; batch related new-premise reviews and reuse only matching valid reviews to keep cost bounded.

Before delivery, an atomic guard checks artifact identity, approval validity and whether an unresolved material-change flag affects the reviewed claims. If stale, pause delivery and re-review/rewrite within budget. Policy can enforce declared bindings/flags, not perfectly determine semantic materiality; uncertain relevant changes conservatively reopen review. A post-delivery contradiction creates a superseding report/correction record, never a silent rewrite of history.

## 7. Rule C: explicit ending and reviewer-failure behavior

Keep diagnosis status distinct from execution/review status:

| Outcome | Meaning and delivery rule |
| --- | --- |
| `reviewed_report` + `cause_supported` | A specific cause/contributors are supported for stated scope; D7 accepted the exact artifact and dependencies remain valid. |
| `reviewed_report` + `cause_unresolved` | Symptom is established but causal evidence is insufficient; D7 can accept an honestly inconclusive report. |
| `reviewed_report` + `complaint_unverified` | Available searches could not establish a matching issue; does not mean the system is healthy. D7 accepted the limitations. |
| `investigation_incomplete` | No currently valid final approval: reviewer unavailable, budget exhausted, orchestration failure or unfinished required checks. Return deterministic status, stop reason, pending work and clearly unreviewed finding references—not an approved causal narrative. |

Reserve configured budget for writing/review but do not promise it is always sufficient. All retries/rework count against global limits. Failed or absent review is never `accept`. A model is not required to generate the fallback status. If an earlier approval is still valid for the exact current scoped artifact, delivery can use it; otherwise incomplete is safer than pretending review succeeded.

Within budget, D1 can change source/query/scope, retry transient failures or ask clarification. It cannot retry until a critic agrees. Persist a checkpoint and stop reason. Explicit human/user resumption can create new tasks from the checkpoint; do not run an unbounded background investigation after reporting completion.

## 8. Self-audit and security

Use the [question-grounding contract](question-grounding.md): distinguish known premises, exploration and unknowns, and make task origins visible. Review new read/architecture premises before they constrain cross-domain work, flagged contradictions/prerequisite gaps, causal promotion and final delivery. D7 may batch related checks; neutral discovery can continue while uncertain premises stay unverified.

Enforce read-only source capabilities, tenant filtering, resource limits, privacy/secret redaction and tool parameter validation outside the model. Source documents, logs, prompts and code comments are untrusted evidence, never instructions to broaden permissions or call arbitrary tools. Shared caches include trusted authorization and source/time/version identity and invalidate on relevant changes.

## 9. Planned integration tests

These are acceptance criteria, not executed behavioral tests:

- Late result for group A cannot explain new group B; unchanged independent code results are not needlessly discarded.
- Two result handlers cannot overwrite one another's accepted revisions; duplicate events do not duplicate facts, delivery or cost accounting.
- A draft approved before contradictory evidence cannot pass the delivery guard. Unrelated evidence does not automatically revoke all reviews.
- Editing approved report bytes, scope, recommendations or supporting claims requires valid updated review; delivered reports remain immutable history.
- D7 timeout, malformed verdict, denied source or exhausted budget cannot become approval. The incomplete status works even if D1/D8 fails.
- Partial source reads do not become absence claims; relevant late data reopens affected conclusions.
- Invented components/irrelevant citations/omitted prerequisites are challenged; measure review escape rates rather than assume perfect detection.
- Independent tasks really overlap; dependent tasks wait for prerequisites. Every role/attempt consumes the same global budget.
- Baseline receives the same tools, permission scope, evidence availability and failure replay; report all model/review costs.

## 10. Research boundary

The lifecycle fields and policies above are our proposal. Anthropic documents scoped delegation and asynchronous coordination challenges; incident.io documents findings that can be overturned; Resolve documents independent verification. PostgreSQL documents concurrency/snapshot behavior, not our report-approval protocol. See [research and reanalysis](agent-contract-research.md) for primary links, distinctions and unresolved implementation choices.
