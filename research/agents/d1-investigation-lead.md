# D1 — Investigation lead: reasoning and orchestration

Status: proposed contract, not an implemented/tested agent. [Agent guide](README.md) · [Shared protocol](../agent-protocol.md). D2 is removed; D1 explicitly owns cross-source reasoning as well as coordination.

## Purpose and boundary

Discover what the complaint refers to, build a partial source-backed working map, maintain competing explanations, choose useful questions and coordinate selected investigators. Do not start with a known correct path or prewritten diagnosis. D1 is not a routing-only agent, a bulk source reader or its own independent approver.

## What D1 receives and can access

Initial input is `report_text` plus trusted setup: identity/access scope, role/tool registry, directory handles, empty case state and limits. Subsequent invocations use current case snapshots and accepted result references. No service, environment, incident time, logs or answer is secretly attached to the user's complaint.

Navigation tools: `catalog.search`, `catalog.describe`, `history.search`, `case.read`, targeted `evidence.fetch`, `delegate_task`, `request_clarification`. D1 can retrieve originals for important reasoning but delegates deep source searches. These are proposed interfaces; source authorization and budgets are enforced outside the model.

## Dynamic work loop

1. Inspect available capabilities; search authorized metadata with feature terms. Keep multiple candidates, source freshness and search assumptions.
2. Choose discovery questions suited to the complaint. D3 is not always first: wrong AI answers can justify D6 discovery even with healthy infrastructure. D4 can locate an unknown feature implementation without a filename.
3. Record learned entities/relationships and their sources, exploratory assumptions, unknowns and suggested follow-ups from specialists. Learn a read contract before naming its fields in concrete data queries.
4. Compare explanations; prioritize a question by its ability to distinguish them, available evidence and cost. Parallelize independent tasks; do not invoke every agent by default or insist on three hypotheses.
5. Read results only after structural/authorization/applicability checks. Reconsider claims when scope, dependencies or relevant evidence changes. Preserve contrary evidence and unexplored candidates.
6. Request required D7 premise/causal review. A rejection becomes targeted follow-up, narrower scope, clarification or an inconclusive outcome—not a rewritten guess.
7. Ask D8 for a scoped draft; obtain valid final D7 review and delivery-guard success. Deliver the exact approved artifact, or allow deterministic incomplete status if final review is unavailable.

## Exact runtime input, tools and structured answer

Runs as a logical task in the investigation backend, not a separate VM or preloaded copy of the application. The backend executes tools and calls the model repeatedly. [Runtime and source locations](../runtime-and-tools.md).

Full required Task-v1 + AgentAnswer-v1 + trusted Result-v1 fixture: [d1-example.json](../contracts/d1-example.json). Exact machine-readable types: [agent-io.schema.json](../contracts/agent-io.schema.json). The fixture is synthetic, not evidence or a mandatory execution order.

The task-specific `role_input` sent to this agent is:

```json
{
  "trigger": "bootstrap",
  "report_text": "The customer group did not receive the message.",
  "case_snapshot_ref": null,
  "new_result_refs": []
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
| `delegate_task` | Validate a task proposal, reserve budget and enqueue it once; runtime assigns IDs/revisions. |
| `request_clarification` | Record and present a focused missing-scope question to the user. |

Every argument, returned `data` field, source backend and guard is specified in the [tool catalog](../tool-catalog.md). Tool errors/coverage are connector-owned receipts, distinct from the agent's interpretations.

The model returns shared fields `agent_id`, `execution_status`, `observations`, `interpretations`, `unknowns`, `coverage_receipt_refs`, `suggested_followups`, plus this role's required `lead_decision` object:

```json
{
  "action": "delegate",
  "knowledge_delta": [
    {
      "text": "Catalog search returned a candidate delivery service, not a confirmed incident match.",
      "kind": "observation",
      "evidence_refs": [
        "E0"
      ]
    }
  ],
  "hypothesis_updates": [],
  "dispatched_task_refs": [
    "task:D3-discovery"
  ],
  "clarification_ref": null,
  "report_ref": null,
  "decision_reason": "Investigate matching attempts before naming a failing component or cause.",
  "stop_reason": null
}
```

This is the exact role-specific object; the linked fixture contains the whole answer and runtime wrapper. Unknowns remain explicit even on `complete` tasks. Runtime validates requested agent identity and source references, adds trusted task/revision IDs, actual tool errors and measured costs, then performs applicability checks before D1 uses the result. A well-formed JSON answer is not proof of semantic correctness.

## Failure and stopping

A late result from old scope cannot silently update the current explanation. Unchanged independent results can be reused after applicability checks; global case-revision changes alone are not automatic rejection. Tool/model/review retries consume shared limits. If progress stalls, change a justified source/query, clarify or stop. No valid final approval means incomplete status, not an approved root cause. D1 cannot grant permissions, change source evidence or certify its own result.

## Planned acceptance tests

- Starts from vague text and navigation capabilities; does not assume a repository, trace or incident time.
- Delegates an unknown-implementation question before field-specific diagnosis; accepts useful specialist-proposed follow-ups.
- Supports different valid investigation paths and AI-quality incidents without error logs.
- Handles old-scope/duplicate/contradictory results, missing history and reviewer outage without inventing support.
- Stops within aggregate limits; counts all specialist, review and writing costs; never changes approved report bytes on delivery.

## Research basis

Anthropic's research system describes delegation with objectives, output expectations, tool/source guidance and boundaries. This motivates explicit assignments; its research results do not validate our incident system. [Primary account](https://www.anthropic.com/engineering/multi-agent-research-system). Exact tools, lifecycle decisions and D1's merged responsibility above are our proposal.
