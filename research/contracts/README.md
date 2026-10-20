# Machine-readable agent and tool contracts

Status: design artifacts only. No agents, cloud adapters or behavioral evaluation are implemented here. All example identifiers/evidence/content are synthetic fixtures. Do not use them as real incident evidence.

## Files

| File | Exact contents |
| --- | --- |
| [agent-io.schema.json](agent-io.schema.json) | Strict Task-v1, model-produced AgentAnswer-v1, runtime-produced Result-v1, seven role-specific input/output types, shared read-contract and evidence types. |
| [tool-contracts.json](tool-contracts.json) | Every tool's name, eligible agents, source backend, purpose, strict input/data schemas and guards. |
| [tool-receipt.schema.json](tool-receipt.schema.json) | Common runtime-owned tool response, error, coverage and cost envelope. |
| [d1-example.json](d1-example.json) | D1 bootstrap input, post-discovery structured decision and wrapped result. No service/time/table/cause is supplied at bootstrap. |
| [d3-example.json](d3-example.json) | Observability discovery input/output. |
| [d4-example.json](d4-example.json) | Implementation investigation and discovered code-to-data ReadContract. |
| [d5-example.json](d5-example.json) | D5 receives the read contract and cited code; returns current data without inventing historical proof. |
| [d6-example.json](d6-example.json) | AI behavior input, retained step comparison and unresolved tracing/mapping gap. |
| [d7-example.json](d7-example.json) | Independent review rejects premature causal attribution. |
| [d8-example.json](d8-example.json) | Cause-unresolved report content and stored draft reference; no writer approval. |
| [failed-result-example.json](failed-result-example.json) | Trusted failure result with no model answer; timeouts do not fabricate findings or reviewer acceptance. |
| [tool-flow-example.json](tool-flow-example.json) | Exact tool requests/receipts for versioned code read → replica identity → schema → scoped current row; also a timeout alternative. |
| [definitions.mjs](definitions.mjs) | Editable source for the proposed schemas/tool registry. |
| [build-contracts.mjs](build-contracts.mjs) | Generates JSON contracts, fixtures, tool catalog and per-agent insert text from the source definitions. |
| [validate-contracts.py](validate-contracts.py) | Schema/example, role/tool wiring and negative-fixture checks; requires Python jsonschema. Does not run agents or source queries. |
| [check-doc-links.mjs](check-doc-links.mjs) | Local Markdown/HTML link and fragment checks, HTML ID uniqueness and overview roster/tool-count consistency. |

Every listed property in a strict object is required. Unknown optional information uses explicit null where permitted; empty collections use `[]`. References are opaque registry IDs with versions, not credential handles. Time strings in examples are UTC; runtime must additionally validate parseable ordered time intervals and source-specific identifiers. Schema validation alone cannot establish authorization, referential integrity or causal support.

Do not send this entire registry/schema bundle to each model. Select the requested role's answer schema and permitted tools, resolve/prune their needed definitions, and adapt to the model provider's supported schema subset. These are application-level contracts, not a claim that every provider accepts the full schema unchanged. Local validation is still required after structured generation.

## Distinguish three outputs

1. A connector returns ToolReceipt: actual source response, coverage, error and measured tool cost. Runtime registers original evidence independently of model prose.
2. The LLM returns AgentAnswer-v1: findings/interpretations plus its role-specific object. It does not set trusted task IDs, elapsed time, hashes or approval state.
3. Runtime constructs Result-v1: trusted task/attempt/scope/dependency identity + `answer_state` + the validated model answer + receipt references + actual errors/cost. `answer_state=valid` requires an answer; `unavailable`, `invalid` or `cancelled` uses `answer=null`. Actual errors/receipts survive a model failure without fabricated findings. Runtime then checks late-result applicability under the [shared protocol](../agent-protocol.md).

`observations[].id` and interpretation IDs are task-local labels, not registered evidence/claim IDs. Runtime assigns versioned claim/artifact IDs on ingestion. A D4 ReadContract is source-backed candidate content; runtime registers its artifact reference only after validation/applicability checks. The next D5 task carries that reference plus useful cited excerpts. Runtime review policy must approve new premises before they constrain cross-domain work.

## Runtime rules beyond JSON Schema

- Validate requested role and mode, then intersect role tools, actual capabilities, trusted identity/tenant/source permissions, task scope and global budget.
- Validate `delegate_task.proposal.role_input` against the proposed target role. Runtime allocates task IDs/revisions and an idempotent queue record. D1's final `dispatched_task_refs` records already-created tasks; never dispatch those twice from its answer.
- D7 `target.kind=report` requires the exact stored report/hash/manifest and current scope; `claims` requires particular claim revisions. Runtime binds verdict to the target; agent text cannot mint approval.
- D8 calls `report.store_draft` with structured content. Runtime validates references, canonicalizes and hashes the stored artifact. The returned draft ID/version/manifest must match D8's final answer and submitted content. If storage fails, return null identities, failure/partial status and issues; do not invent them.
- Validate evidence/receipt/artifact references against original connector records, source/tenant/time/revision and role access. Preserve covered versus unsearched scope. An existing citation can still be irrelevant.
- Validate filter types against discovered schema, forbid unauthorized operators/functions, enforce scan/time/row/byte limits and cursor/snapshot semantics. A plain read-replica query is never historical time travel.
- A complete task is not a proved cause; `partial` and `failed` are not empty success. D7 verdict `insufficient` is a completed review, not necessarily an execution failure.
- Final delivery uses the immutable artifact and valid exact-target D7 approval. Without valid approval return deterministic incomplete status, including if the model or reviewer is unavailable.

## Rebuild and check

```text
node research/contracts/build-contracts.mjs
python research/contracts/validate-contracts.py
node research/build-overview.mjs
node research/contracts/check-doc-links.mjs
```

Generated `*.insert.md.txt` files are reviewable snippets for updating the seven hand-maintained agent docs; generating schemas does not silently replace those documents. Proposed source connectors/agent runners still require separate implementation and real evaluation.
