# Agent contracts: start here

Current design: **seven agents, no D2**. D1 owns reasoning and orchestration. These are researched design contracts, not runnable agents or tested prompts. Each role has stable expertise but receives dynamic discovery, diagnosis or verification tasks—not a fixed incident script.

Start with [how the agents actually run](../runtime-and-tools.md): one backend can host all seven logical roles, calling an LLM and executing real source-query tools. Code stays in repositories/checkouts/indexes; data stays in the approved replica; telemetry stays in configured cloud/log stores. The model receives only selected results. Then read the [exact tool catalog](../tool-catalog.md) and [structured schemas + complete JSON examples](../contracts/README.md) as needed.

## Read one agent at a time

| Agent document | Its distinct responsibility |
| --- | --- |
| [D1 — Investigation lead](d1-investigation-lead.md) | Bootstrap discovery, maintain competing explanations, delegate, synthesize and stop. |
| [D3 — Observability](d3-observability.md) | Establish observed behavior and coverage through telemetry/outcome evidence. |
| [D4 — Code, deployment and infrastructure](d4-code-deployment.md) | Discover actual implementation, cross-repository wiring, effective changes and runtime bindings. |
| [D5 — Database and data](d5-data.md) | Check the discovered read path, actual scoped values, history, consistency and DB behavior. |
| [D6 — AI behavior](d6-ai-behavior.md) | Investigate actual prompts, context, tools, decisions and application-agent coordination. |
| [D7 — Independent critic](d7-critic.md) | Challenge premises/causes, demand missing checks, and review exact versioned artifacts. |
| [D8 — Report writer](d8-report-writer.md) | Produce a concise scoped report without adding new causes or claiming approval. |

Read the [shared protocol](../agent-protocol.md) once for common inputs/outputs, permissions, late-result handling, approval invalidation and safe stopping. [Research reanalysis](../agent-contract-research.md) explains sources and decisions. The [HTML overview](../architecture.html#agent-contracts) links to browser-readable versions of every contract.

## Interaction in one picture

```text
Complaint + trusted setup
          |
          D1 <---- navigation directory + case state
          |
          +---- selected D3 / D4 / D5 / D6 tasks
          |                  |
          |          source-backed findings + unknowns
          |                  |
          +<--- validate/applicability check <---+
          |
          +<---- D7 premise / causal challenge
          |
          D8 drafts --> D7 exact report review
                              |
                    valid delivery guard
                              |
                         D1 --> user

No valid final review --> deterministic incomplete status
```

D7 can request evidence through D1 and use authorized originals/verification queries; it does not silently spawn another investigation team. Specialists can recommend cross-domain work, but D1 owns dispatch. Ordinary runtime code enforces permissions, budgets, revisions and delivery rules; it is not another reasoning agent.

D4 and D5 are not knowledge silos. D4 returns a discovered ReadContract (code revision/location, connection identity, relation, keys, predicates, selected fields, transformations/failure behavior and unknowns). D1 includes that shared artifact and cited code excerpts in D5's task. D5 can fetch originals and inspect schema; unknown application usage returns a targeted D4 follow-up. Neither agent must already know code/table names before discovery.

## Corrected example route

Only input: “Messages aren't reaching the customer group.” Values below are illustrative, not a live diagnosis.

1. D1 searches authorized source metadata; D3 finds a candidate attempt ending in recipient-resolution failure. D1 does not yet know the lookup implementation.
2. D4 explains the relevant deployed lookup and its read source. D7 checks new read-contract premises before cross-domain use.
3. D1 can now ask D5 about that read scope and D3 about actual execution; independent questions can run together.
4. D1 compares explanations grounded in their findings. A current row does not prove historical state; D7 checks required causal links, and D5 can receive a historical follow-up.
5. D8 drafts the supported explanation/limits. D7 reviews exact bytes and dependencies. A materially changed premise or report invalidates approval; a late old-scope result cannot silently change the current explanation.
6. D1 delivers the valid reviewed artifact, or runtime returns incomplete status if valid review is unavailable. D6 is called only if AI behavior is implicated; not all agents run every time.

## What each individual document contains

Purpose/boundaries; initial knowledge; dynamic loop; a per-role exact tool table; the actual role_input JSON and structured role-specific answer; links to a full Task/AgentAnswer/trusted Result fixture and strict schema; failure/stopping; planned tests; source rationale. Tool catalog gives every operation's inputs, outputs, queried backend and guards. No contract presumes a full application map, healthy run, complete logs or known cause.
