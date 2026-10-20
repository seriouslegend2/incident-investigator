# Next discussion: agent contracts and implementation choices

The current top-level direction is seven agents: D1, D3-D6, D7 and D8. D2 is removed; reasoning is part of D1. This note no longer asks us to choose a separate analyst or restart the A-D architecture debate. It remains a design, not an implemented or benchmarked system.

## Read next

Start with the [HTML contract overview](architecture.html#agent-contracts), [agent guide](agents/README.md) and [D1 contract](agents/d1-investigation-lead.md). Then review D3-D6, D7 and D8 individually. [Shared protocol](agent-protocol.md) is the common interface/lifecycle reference; [research reanalysis](agent-contract-research.md) records primary-source findings and our decisions.

## Decisions already made in the discussion

- Only vague report text is required; source connections, role/tool registry and authorization are trusted setup, not hidden incident hints.
- D1 has navigation tools and discovers candidate scope. Specialists explain implementation before concrete field/dependency tests; no guessed correct flow.
- Stable roles receive dynamic bounded tasks; not every agent runs, and independent questions may run in parallel.
- Competing explanations, source/assumption distinctions, original evidence, uncertainty and inconclusive outcomes are explicit.
- Code, effective deployment/config/infra, actual DB/data and AI behavior are supported scope; indexes/federated retrieval address large multi-repository estates.
- Late results require applicability checks; material evidence/report changes invalidate approval; reviewer failure without valid approval returns incomplete status.
- Production access is read-only and scoped. No autonomous remediation, permanent per-agent monitor or proof of zero hallucinations.

## What to decide during implementation

| Decision | Concrete question |
| --- | --- |
| D1 bootstrap | What exact role/tool descriptions, catalog fields and metadata-search fallbacks are supplied? |
| Source adapters | Which simulated code, telemetry, data, deployment/config and AI sources expose the proposed capabilities first? |
| Common schemas | How are Task/Result, scope/dependency versions, source snapshots, coverage and role extensions validated? |
| Case state | Which transaction/version strategy enforces late-result handling and atomic delivery checks? |
| Review granularity | Which premises are batched, when can reviews be reused, and how is material change detected/measured? |
| Models/framework | What implementation best supports bounded tasks, recovery and state without unnecessary infrastructure? |
| Budgets | What per-source/query/task/global limits and writing/review reserves are justified by tests? |
| Evaluation | Which held-out incidents exercise retrieval misses, code/data/AI faults, stale results, review outage and proper abstention? |

Run source/tool and lifecycle tests before broadening the UI. Compare against the same-tools single agent and a simpler supervisor policy; measure all model/review calls and backend retrieval cost. Individual documents contain planned acceptance criteria, not completed tests or frozen prompts.
