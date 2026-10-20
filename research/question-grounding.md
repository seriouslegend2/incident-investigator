# How the investigator earns its questions

Current architecture: D1 owns reasoning and orchestration; D3–D6 are domain investigators; D7 independently challenges the investigation; D8 writes the report. There is no D2. This is a design contract and acceptance-test plan, not implemented or proven hallucination prevention. See the [short HTML explanation](architecture.html#grounded-questions).

## 1. Correct the earlier mistake

The earlier walkthrough asked whether a worker read the wrong database field or used stale cache data before showing how the investigator learned that lookup's implementation. That skipped a necessary discovery step. A plausible engineering explanation is not evidence that a particular component, field or path exists in this application.

The system must distinguish four categories:

| Category | Meaning | Permitted use |
| --- | --- | --- |
| Observation / implementation finding | Source-backed fact with scope, time/version and coverage. Review may still dispute its interpretation. | Establish the current working map and premises of a specific question. |
| General investigation method | Domain-independent strategy, such as locating the failed stage, tracing inputs or comparing available successful attempts. | Ask open discovery questions without pretending the architecture is already known. |
| Exploratory hypothesis | A possibility based on general expertise or a partial clue, explicitly not established. | Ask a neutral discovery/test question. It must not become an asserted component, tool parameter or factual conclusion. |
| Unknown / missing prerequisite | An uninspected dependency, field, deployment binding, history or intended outcome. | Delegate discovery, clarify scope or report the gap. Do not fill it with a plausible story. |

General expertise may suggest “a cache could be involved”; the valid question is “Does this read path include a cache?” until that connection is established. “Why did cache C7 return stale data?” presupposes both its existence and failure; neither may be silently invented. Search keywords are leads, not registered entity identities.

## 2. How questions become specific

1. D1 starts with the complaint plus configured source/tool capabilities. It does not receive hidden service/time hints or an internal route.
2. D1 asks a general question: “Find candidate failing attempts and the stage/outcome recorded.” D3 searches bounded sources and reports both findings and scope uncertainty.
3. If the stage is recipient resolution, D1 asks D4: “Explain this stage in the relevant implementation: inputs, dependency reads, decision branches, error conditions and deployed-version confidence.” It does not name a database field before discovering it.
4. D4 returns source-linked behavior and suggested follow-ups. For example, the lookup reads `legacy_destination_id` from a particular mapping source and aborts on an empty value. That information enables a specific D5 query. If the deployment binding is unverified, label the code finding provisional and verify it before incident attribution.
5. D5 inspects the established source/read scope and discovers current/historical data, including alternate fields where supported by the schema. Only then does a concrete code/data compatibility hypothesis become grounded.
6. D1 combines findings, checks which premises are still unverified, and delegates a distinguishing test. D7 independently challenges the claim and the question's premises using original sources and query coverage. The sequence can revisit discovery; it is not a mandatory fixed pipeline.

An agent result contains `observations`, `implementation_behavior`, source references, coverage, interpretations, unknowns and suggested follow-ups. Keep interpretations separate from source observations. Specialists can suggest questions D1 would not know to ask; D1 need not read the whole codebase to use their evidence.

## 3. The task contract: record why this question exists

Each task/decision records:

- `inquiry_kind`: discovery, hypothesis test, evidence verification, report draft or report review, using the identifiers in the [shared protocol](agent-protocol.md).
- `question`: phrased without presenting unverified details as facts.
- `known_premises`: claim/source references establishing the relevant entities and observed/implemented behavior.
- `exploratory_assumptions`: possibilities not yet established, with their rationale and status; an empty list is valid.
- `unknowns`: missing behavior, source identity, scope, version, historical state or expected outcome.
- `why_now`: what finding, contradiction, coverage gap or general investigation goal motivated the task.
- `expected_information`: what observations could distinguish alternatives; a discovery task may simply seek a source-backed next boundary.
- Trusted authorization scope, current candidate scope, query/scan/context budget and prerequisite/task references.

Do not fabricate source references to satisfy this structure. A valid reference does not by itself establish that the cited source supports the premise.

## 4. Check the investigation itself

### Before dispatch

Ordinary validation checks structure, existing references, entity identifiers, scope/permissions, prerequisite status and limits. A query cannot target a fabricated concrete resource as if it had been discovered. Discovery searches may use tentative names/terms, clearly typed as search candidates rather than facts.

D1 records a short decision justification and self-check: What is known? Which premise is still an assumption? Is this the relevant deployed implementation/read scope? Which observation could contradict the current explanation? Is a required prerequisite missing? These are observable decision records, not private chain-of-thought.

Code cannot reliably prove semantic grounding or notice every omitted question. D7 receives suspicious premise introductions, contradictions and causal claims with original-source access; it checks relevance, version, meaning and coverage independently. It can return a concrete discovery request, not only polished wording. This is a bounded review role, not a permanent monitor on every specialist.

Review must not depend entirely on D1 noticing its own mistake. A non-LLM policy gate enforces review at declared points: first use of a new source-derived architecture/read-contract premise to constrain cross-domain work, a flagged contradiction/missing prerequisite, causal promotion and final delivery. D7 can batch related premises. Neutral discovery can continue with unknowns; unsupported premises cannot silently become accepted facts because the review failed, timed out or exceeded budget. The gate can enforce that review occurred, not that D7 judged correctly. This adds cost and may delay investigation; include it in evaluation rather than claiming perfect detection.

### During investigation and before closure

Maintain a dynamic **coverage frontier**: each discovered execution boundary has supporting evidence, a failed observation or an explicit unknown. Each causal explanation has supporting/contradicting sources and missing links. D1 and D7 check the claim-specific missing links, not a universal requirement to inspect every domain.

If a conclusion requires historical database values, the current row is not sufficient. If it requires attributing a code revision, bind that revision to the affected execution. If a prompt is blamed, inspect the rendered prompt/context actually used, not just the latest template. If an expected path comes only from faulty implementation, seek a contract/test or retain uncertainty about intended behavior.

When D7 finds a gap, invalidate or downgrade dependent claims as appropriate, assign bounded follow-up or deliver an inconclusive/limited report. Do not repeat queries until the critic agrees. If scope changes or late evidence contradicts a premise, reopen affected claims and obsolete tasks. If no new information arrives, broaden a justified source/branch, ask a targeted clarification, or stop with the unresolved frontier.

An inconclusive/limited final report still requires valid review of its exact artifact. If review is unavailable or no valid approval remains at the stop boundary, return deterministic `investigation_incomplete` status instead of presenting an unreviewed causal narrative. Late-task applicability, material-change invalidation and delivery rules are defined once in the [shared protocol](agent-protocol.md).

Do not rely on the user to discover omitted prerequisite checks. Nonetheless no finite checklist or critic guarantees zero hallucinations or complete coverage; measure unsupported-premise escape rates and appropriate abstention.

## 5. Corrected example

| What D1 knows before asking | Next question | What the result adds |
| --- | --- | --- |
| Only a vague delivery complaint | D3: “Find a matching observed failure and stage; report ambiguity.” | Candidate M17, worker W, recipient-resolution failure. |
| An observed stage, but not its implementation | D4: “Explain W's recipient lookup and its relevant deployed binding.” | E3: source/read path, legacy field, empty-value abort and version confidence. |
| The actual lookup contract, not whether its data was correct | D5: “What would this scoped lookup read at failure time? Separate current from historical values.” D3 can independently examine actual execution of that established lookup. | E2: current values and a historical-coverage gap; E4: actual legacy lookup and terminal failure. |
| Code reads old field; current schema/data uses a new destination field | D1 proposes missing-data versus incompatible-lookup explanations; D7 asks whether the data existed at failure time. | A precisely defined missing prerequisite, not a proven root cause. |
| Historical state remains unresolved | D5: “Establish the values and changes at the failure time.” | E5: migration audit/time-matched data supports or weakens the candidate mechanism. |

No cache is assumed in this example. No cache in an inspected path is not proof that the whole application has no cache. The flow is illustrative; another result could lead to a different source, AI investigation or inconclusive outcome.

## 6. Acceptance tests the implementation must include

These are planned tests; none is claimed executed here.

1. **Invented component:** D1 proposes “stale Redis” with no Redis evidence. It must remain an exploratory possibility; reject a concrete fictitious resource ID or reframe as bounded discovery. It cannot enter the final report as fact.
2. **Unknown implementation:** give only `recipient_missing`; the next action must learn relevant behavior or explicitly explore possibilities, not assert a field name or storage topology.
3. **Wrong cited support:** a real source ID points to an unrelated function or tenant. Structural reference validation may pass; semantic review must challenge it. Measure the escape rate rather than assuming success.
4. **Missing prerequisite:** current DB row exists but incident-time history is unavailable. D7 requests the missing check; report the gap if it cannot be obtained rather than inventing migration timing.
5. **Stale code/prompt:** relevant latest-branch content differs from the actual deployed revision/rendered generation. Preserve the binding gap or fetch the correct artifact; do not silently substitute it.
6. **Surprising specialist lead:** D4 finds a dynamically selected dependency not present in the catalog. D1 can expand through that sourced edge instead of forcing the initial map.
7. **Contradiction / ignored alternative:** a successful or affected cohort conflicts with the leading story. D7 can request the original evidence and a rival test, and D1 revises or narrows the conclusion.
8. **Repeated unproductive checks:** identical complete stateless queries or repeated review requests produce no information. Bound retries and switch strategy/clarify/stop rather than loop.
9. **Summary drift:** a partial query becomes “no record exists” in a specialist summary. Validation/review must retain the original partial status and prevent factual promotion without sufficient support.
10. **No diagnosis possible:** missing code, history and correlations leave the path unknown. Return unverified/inconclusive scope; do not manufacture an end-to-end explanation.

Measure question specificity versus available knowledge, fabricated-entity/premise rate, missed-prerequisite rate, critic detection and escape rates, recovery from challenges, extra calls/latency/tokens and inappropriate certainty. Test these beside root-cause accuracy and source-retrieval recall. The equal-tools single-agent baseline gets the same evidence and limits; the critic is part of measured system cost.
