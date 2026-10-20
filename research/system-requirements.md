# Our system requirements

Implementation contracts: [runtime/source locations and execution loop](runtime-and-tools.md), [exact tool catalog](tool-catalog.md), [machine-readable input/output schemas](contracts/README.md). Code, deployment, logs and replica data are queried through real configured connector functions; the LLM only receives bounded results. D4 and D5 share a discovered read contract and supporting code/schema evidence, not isolated knowledge.

This is the current scope established in the discussion. The [HTML guide](index.html) is the main scope file; the [visual architecture](architecture.html) shows dynamic routing and review loops. The original PDF supplies the assignment minimum; the requirements below also include the user's codebase, database/data, infrastructure, and AI application scope. The current seven-agent direction is recorded in [individual agent contracts](agents/README.md); its implementation, framework and measured performance remain unvalidated.

## Large-estate design target

Design for many repositories, connected services, billions of organizational code lines and millions of telemetry records—not a single monorepo loaded into an LLM. The [scale architecture](architecture.html#large-estate) and [detailed design contract](scalable-design.md) define the updated approach. This is a design target, not an implementation or measured scale claim.

Prepare searchable source/service metadata, incremental repository/revision indexes, artifact-to-source/effective-config mappings and source-native telemetry/data/AI adapters before incidents. At incident time, discover candidate workflows, aggregate outcomes, locate an attempt/cohort and follow relevant cross-service boundaries. Retrieve exact versioned code slices and scoped originals; expand deliberately when evidence is insufficient. One service may span several repositories/artifacts; each service's active revision must be resolved independently.

Distinguish the incomplete estate map, the bounded incident working map and a tested causal explanation. Bound backend scan work as well as response size; expose index freshness, partial results, retention, sampling and uninspected candidates. D1 keeps compact claims/frontier/source references, not all raw history. D7 can challenge retrieval scope and request another candidate/source. Authorization and shared budgets apply to every role, parallel branch, fetch and cache entry.

Large-estate access without indexing, discoverable identity/relationships or retained evidence can be inconclusive; do not promise exhaustive discovery or constant cost. Measure retrieval recall and backend/index resource costs separately from diagnosis and tokens. A small simulated assignment prototype can preserve these contracts but cannot establish billion-line production capacity.

## Input and purpose

Only `report_text` is required: for example, “checkout seems broken” or “the agent gives wrong answers.” No service, environment, time, run ID, logs, or evidence must accompany it. Source integrations and a discoverable environment catalog are configured separately.

D1 is not blind: trusted setup supplies the role/tool registry, authorization scope, bounded directory/navigation tools, case state and limits. Its direct access includes candidate metadata search, case/history reads and targeted original-evidence fetch; deeper code/telemetry/data/AI inspection is delegated. Stable roles do not imply fixed tasks or a mandatory agent sequence. The [shared protocol](agent-protocol.md) defines common task/result fields and permissions.

Discover what the complaint could mean, find a matching observed issue, establish affected workflow/systems/runs and timing, then investigate causes. Keep multiple interpretations when necessary. Ask a targeted clarification if available evidence cannot distinguish them. An unverified complaint and a verified symptom with an unresolved cause are distinct outcomes.

## Discover the path; do not assume D1 already knows it

D1 knows the configured investigation capabilities and source catalog, not a correct internal route for every feature. It delegates discovery and builds a partial, source-backed map:

1. D4 searches service/repository catalogs and versioned code for the reported feature's entry points and callers. D6 follows AI tool definitions/run steps when an AI application initiates the feature.
2. D4 follows actual call sites, event schemas and effective routing/configuration to downstream handlers. D5 checks data lineage, outbox records or database triggers where relevant. A code publish call plus its configured queue and a consumer subscription supports a connection; a plausible component name does not.
3. D3 correlates the candidate attempt's request/job/message IDs, queue/worker events and telemetry. Bind each link to tenant, environment, time, instance and deployed code/config. Async producers and consumers may use linked contexts, not one trace ID.
4. Compare documented contracts/tests with implementation and execution. Code shows what the software implements; it is not automatically proof of what the product should do. Mark inferred expectations and unsupported edges. D7 can inspect original sources and challenge links, and D1 clarifies scope or reports gaps when evidence is unavailable.

A dependency catalog, runbook or historical incident can seed this search, but may be stale. It does not pre-identify the faulty service or supply the answer. D1/history-tool ownership covers historical lookup; analogies propose tests rather than establish today's cause. Do not require a full application map before investigating a verified local failure.

## Compare expected and observed behavior, then explain the difference

Keep three distinct artifacts: (a) a provisional expected workflow with source/assumption labels; (b) an observed execution path with failures and unknowns; (c) candidate explanations for their divergence. A comparable successful attempt is useful contrast, **not required user input or a prerequisite**. If none exists, investigate using supported contracts, code/config and runtime evidence; do not invent a healthy run.

For an illustrative messaging application, the discovered path could be `request → job → queue → worker → destination lookup → provider acceptance → delivery outcome`. Other applications may have different ordering, branches, retries or no queue. Customer visibility is a separate outcome; an API success or delivery status has channel-specific semantics.

At each boundary retain expected behavior, observed behavior, source references, correlation IDs, scope/time/version and coverage/unknowns. Find the first **localized, verified** divergence, or identify an evidence gap—not necessarily the earliest fault in the whole system. Failure localization is not causal attribution. Test explanations such as missing data, a wrong deployed lookup, stale configuration or an upstream handoff defect. Compare affected and healthy attempts/cohorts when available, explicitly noting differences in tenant, payload, load, time, schema and version. Temporal proximity or one good/bad comparison alone does not prove causation.

Missing spans/records, query truncation or retention gaps do not establish nonexecution. Preserve explicit `empty`, `partial`, `timeout`, `denied` and `failed` statuses. A stopped attempt does not establish that all retries or all customer groups failed.

## Ground questions and audit the investigator itself

The [question-grounding contract](question-grounding.md) corrects a prior walkthrough that suggested wrong-field/cache questions before establishing the implementation. D1 starts with general investigation methods, not hidden application knowledge. Specialists explain relevant source-backed inputs, dependencies, decision branches and failure conditions; D1 then uses those findings and their suggested follow-ups to ask specific questions. Discover the actual read source/contract before targeting its fields or data. Generic hypothesis exploration is allowed, but does not establish that an application component exists or failed.

Each decision/task separates `known_premises` with source/claim references, `exploratory_assumptions`, `unknowns`, `inquiry_kind`, `why_now` and `expected_information`, plus scope/prerequisites/budget. “Does a cache exist in this path?” is an exploratory discovery question; “Why did cache C7 return stale data?” is unsupported if that resource/failure has not been established. Concrete query IDs and evidence references must be real, while tentative search terms remain explicitly tentative. Never fabricate a reference to satisfy the schema.

D1 records a compact self-check before choosing follow-ups: what is known versus assumed, whether scope/version/read semantics are established, what could contradict the explanation, and which prerequisite remains missing. These are public decision justifications, not private chain-of-thought. Code validation checks structure, reference/ID existence, prerequisite status, authorization and limits; it cannot prove that a source semantically supports a claim or detect every missing question.

D7 independently checks suspicious premises, contradictions and causal/report claims using original sources and the dynamic coverage frontier. The frontier records discovered boundaries, supporting evidence, failures and unknowns; it is not a checklist requiring all domains on every incident. Necessary code/deployment bindings, incident-time data or actual rendered AI context must be inspected or remain gaps before making claims that depend on them. If a premise fails, invalidate/downgrade dependent claims and direct bounded discovery/follow-up, or deliver an inconclusive result. The user should not be the mechanism that detects these omissions.

Declared review gates are enforced outside D1's discretion: a newly introduced source-derived architecture/read-contract premise used to constrain cross-domain work; flagged contradictions/missing prerequisites; causal promotion; and final delivery. D7 may batch related claims, within shared budgets. A failed/unavailable review leaves its claim unverified; nonpresupposing discovery may continue, but no silent promotion occurs. The policy can enforce review and prerequisite status, not semantic correctness. This is targeted claim review, not an extra monitor agent attached to every specialist.

Test the investigators with unsupported component/field assertions, incorrect but real citations, stale versions, missing prerequisites, summary drift and repeated unproductive searches. Measure unsupported-premise/omission rates, critic detection and escape rates, recovery, abstention and cost. No self-check or critic is claimed to guarantee complete investigation or zero hallucinations. No extra analyst or permanent monitor is added; D2 remains removed.

## Required investigation coverage

| Domain | Evidence and questions |
| --- | --- |
| Codebase | Search versioned repositories, deployed files/functions, call paths, data transformations, database queries, retries/timeouts, and diffs. Existing code can fail without a new deployment. |
| Deployment / infrastructure | Actual rollout status and activation, code revision, canaries/rollbacks, instance/resource health, networking/DNS, permissions, connectivity, and infrastructure events. |
| Database / data | Scoped source records and missing/wrong values; integrity, freshness, transformations and caches; schemas, indexes, migrations, query plans, slow queries, locks/waits and connections. Database health alone does not establish data correctness. |
| Configuration | Effective environment values, flags, runtime settings, and history tied to affected instances and times. |
| AI applications | The actual prompt/version, model/version/settings, input/output, retrieved context, tool calls/results, agent routing/handoffs, shared-state revisions, retries, loops, and stop conditions. Task correctness can fail while transport and infrastructure look healthy. |
| Cross-system context | Logs, metrics, service/data dependencies, source catalogs, historical incidents, and affected-versus-healthy comparisons. |

All domains are required capabilities, not mandatory queries on every incident. Coherent simulated repositories, data snapshots, infrastructure events, and AI run histories are sufficient; no live production system is required.

## AI application evidence must be explicit

- Prompt: version/hash, rendered instructions and variable values actually sent in the failing generation, plus available successful-run comparisons.
- Model: provider/model/version where available, sampling and output-limit settings, responses, errors, truncation and usage. A model-name match alone does not guarantee an identical run.
- Retrieval/context: query, filters, index/source versions, returned document IDs and content, freshness, and context actually passed onward. Distinguish missing source data from retrieval selecting the wrong data.
- Tools: schema/version, call arguments, returned values, status/errors, parsing and transformations. A successful API status does not prove the content is correct.
- Coordination: parent/child run and step IDs, routing decisions, ordered handoffs, state before/after updates, retries/timeouts, duplicate work, loops, and termination.
- Correlation: connect the run to its application request, deployed code/settings, and source data at that time. Current snapshots do not prove past values.

These are observable records and artifacts; private model reasoning is not required. Missing run history is an evidence gap and can make attribution inconclusive.

## Proposed responsibility owners

The current architecture has seven roles: D1 Investigation lead (reasoning + orchestration); D3 Observability investigator; D4 Codebase/change/infrastructure investigator; D5 Database/data/dependency investigator; D6 AI behavior investigator; D7 Independent critic; D8 Reporter. Existing IDs are preserved; D2 is retired, not a hidden or optional agent. D1 owns competing hypotheses, cross-source synthesis, distinguishing checks, scope and task priorities. Specialists choose queries, reason locally and propose cross-domain follow-ups rather than merely collecting evidence. The AI behavior role owns prompt/model/retrieval/tool/coordination questions while requesting code/data checks when needed.

Decision: do not retain a separate hypothesis analyst merely to mirror the assignment's role list. Its work is explicitly performed by D1. D7 independently challenges claims, alternatives and source coverage; it does not replace the primary investigator and then approve its own explanation. The PDF names reasoning as a role, but the user's chosen architecture merges that responsibility into the lead rather than implementing a distinct Reasoning Agent. Document this packaging decision accurately; do not falsely claim that the PDF explicitly labels its roles optional examples. Scale-oriented retrieval/indexing changes do not depend on adding another agent.

The [architecture comparison](architecture.html) preserves A, the original supervisor/local-monitor option, B fixed outer stages and C peer handoffs as references. The current direction is D's hypothesis/evidence policy with D1 owning reasoning and orchestration and no D2. A remains a useful simpler evaluation baseline; no measured advantage is claimed. [Research and decision notes](architecture-options.md) explain the distinction.

In D, D1 compares competing causes, chooses distinguishing questions, prioritizes work and budgets, and delegates selected tasks. Ordinary runtime code dispatches work whose prerequisites are satisfied. A shared evidence/hypothesis board records support, contradiction, unknowns, question/task dependencies and review status. Relevant findings or stalls trigger D1 to revise the explanation and plan; specialists still choose their queries and reason within each task. This is not an all-source collection pass followed by one reasoning call.

Stable active IDs in the detailed HTML: D1 Investigation lead, D3 Observability, D4 Code/change/infrastructure, D5 Database/data/dependencies, D6 AI behavior, D7 Verifier/critic, D8 Report writer. R1 Scheduler/supervisor, R2 Investigation store and R3 Result validator are software components, not more LLM agents. D7's claim and final-report reviews are separate calls with fresh context. The [interactive message trace](architecture.html#option-d) uses these IDs consistently; D1's hypothesis updates are its own reasoning steps, not calls to another analyst.

## Local monitors and final review

Both candidates validate schemas, IDs, actual query scope/version, limits and coverage in code for every result. In A, a local task checker reviews specialist work. In D, a shared semantic verifier reviews new claims used to rank causal hypotheses, disputed findings and questionable support; unreviewed claims remain provisional. Each review receives the assigned question, claim and original sources. Return `accept`, `revise`, `insufficient`, or `failed` with concrete requests. Acceptance does not prove a root cause. Reuse checked evidence only while its source version and scope match.

D7 must have authorized access to original sources and unresolved coverage, not only favorable D1 summaries. It can request a specific rival test before causal commitment, for example a historical mapping lookup or provider receipt. Structural separation does not eliminate shared-model bias. Review/rework is bounded and may end with a limited report.

Revisions share task/global budgets; do not retry until a checker agrees. Unavailable sources, agent exceptions and exhausted limits retain partial findings and explicit status. A cross-domain gap becomes a question for D1, which can delegate a targeted follow-up; independent ready tasks may proceed. Checking need not create permanently running extra agents or an infinite hierarchy of monitors. D's conditional semantic review trades fewer potentially redundant checks for more claim-status/invalidation bookkeeping; its benefit must be measured.

Before delivery, the independent final critic reviews the exact report draft, source evidence, alternative hypotheses, contradictory observations, uncertainty and recommendations. It can approve, return specific evidence/revision requests, or accept a limited inconclusive report. The Coordinator delivers the approved artifact without silently rewriting it. A changed report must be reviewed again. Neither local nor global review guarantees zero hallucinations.

## Lifecycle correctness: the three review findings are now explicit

Canonical semantics live in the [shared protocol](agent-protocol.md); every individual agent contract inherits them.

1. **Late parallel results:** task/result IDs, attempt identity, scope revision and specific dependency versions accompany each result. Ingestion checks authorization, structure, duplicates and applicability before claims change. A changed global case revision alone does not discard independent valid evidence. A late result for old group A stays A-scoped history or needs revalidation; it cannot silently explain current group B. Use version-checked atomic updates, not agent overwrites.
2. **Revocable version-bound approval:** D7 review binds the exact report bytes/hash, scope, reviewed claim revisions and evidence/coverage dependency manifest. Material changed/contradicting support, scope or report content invalidates affected approval; unrelated updates need not invalidate everything. A delivery guard atomically verifies current validity. Relevant late evidence after delivery creates a superseding correction record, not silent history edits. Semantic materiality is not perfectly decidable; measure detection and invalidation errors.
3. **Reviewer failure and stopping:** a reviewed inconclusive diagnosis is distinct from an incomplete investigation. `reviewed_report` requires a valid final artifact approval; its diagnosis can be `cause_supported`, `cause_unresolved` or `complaint_unverified`. If review fails, times out or cannot finish within budget and no valid approval remains, return deterministic `investigation_incomplete` status with stop reason, pending work and clearly unreviewed references—not an approved causal report. This fallback must work even if D1/D8 is unavailable.

All attempts and retries consume shared limits; duplicate result delivery does not double-apply findings or double-count an already recorded attempt. Cancelling a task is best-effort, so late-result policy still applies. Budget reservation for final writing/review is configured but cannot guarantee success. Planned tests include out-of-order results, stale report approval, material versus irrelevant updates, duplicate events and reviewer outage.

## Investigation contract

Investigators choose queries, interpret observations, and request follow-ups. Query tools retrieve validated records with provenance and complete/partial/failed status. Each task records its question, tentative scope, rationale, and budget. Shared state keeps raw evidence, revisions, hypotheses, counterevidence, unknowns, and query failures separate.

Delegate questions such as “Was M17 consumed by a worker?” rather than “collect logs.” Each result includes observations, original source references, supported/weakened hypotheses, counterevidence, coverage and any unexpected lead. Preserve source snapshots/references; allow interpretations to become disputed or superseded. Reconsider dependent conclusions and cancel obsolete tasks when supporting findings or scope changes. Multiple summaries of the same source are not independent corroboration.

Do not equate a symptom with a cause, missing evidence with contradiction, repeated summaries with independent observations, or a plausible AI answer with correctness. Rank hypotheses and distinguish initiating faults from contributing failures. Define confidence from evidence and limitations; do not present invented probabilities as calibrated.

The runtime must enforce parallel task dependencies, timeouts, bounded retries, recovery, per-task limits and aggregate budgets. Criticism can trigger another bounded evidence-gathering round. Stop with a valid reviewed report (including inconclusive/unverified-complaint outcomes) or deterministic incomplete status when valid final review is unavailable.

## Coverage limits and safe investigation

Domain names are capabilities to demonstrate, not proof that all faults are covered. Explicitly test async queues/dead letters/retries/duplicates/order, stale caches/replicas/indexes, external permission/rate-limit/delivery failures, client visibility, effective network/config behavior, concurrent faults, false alarms and missing/contradictory telemetry. Use the existing specialists rather than adding one permanent agent per technology. Report the supported event/cohort and remaining blast-radius uncertainty separately.

Enforce tenant-scoped, least-privilege, read-only tools, bounded query ranges/row counts/compute, and secret/PII redaction. Retrieved logs/code/documents/prompts are untrusted evidence, never authority to change investigation instructions or permissions. No deployment, database write, customer message send/retry or production experiment is authorized by a diagnosis request. Recommend actions and conditions; safe replay/testing belongs in the simulated evaluation environment. Record the investigators' own tool/agent failures separately from application faults.

## Example connecting AI behavior and data

For “the agent gives wrong answers,” determine the affected workflow/runs. Suppose the source record exists and the database tool returns it, but a handoff drops a required field and the next prompt substitutes a default. Evidence supports a coordination defect with a prompt fallback as a contributor. A different run could instead have a missing row, stale retrieval, wrong query filter, or malformed tool response. Test these alternatives; do not blame prompts merely because the output is wrong.

The application's agent traces are evidence under investigation. Our investigation agents' own execution traces are a separate audit trail. Both need stable identifiers; neither provides hidden ground truth to investigators.

## Evaluation and submission

At least ten incidents must cover the domains above, including vague reports, misleading evidence, conflicting observations and tool failures. Include cases where code inspection, actual database contents, or AI traces change the diagnosis. Exercise prompt regression, stale/filtered retrieval, bad tool data, lost handoff state, coordination loops and unavailable run history across the suite; scenarios may combine faults.

Include held-out variants for misleading recent deployments, current-versus-incident-time data, provider acceptance without delivery, queue stalls/duplicates, stale cache/replica state, multiple fault cohorts, ambiguous/false complaints and malicious retrieved instructions. Test the path-discovery process and missing healthy-run behavior—not only diagnosis after the correct path is supplied. Beyond required metrics, record scope discovery, boundary localization, appropriate abstention and unsafe tool attempts. Compare the basic supervisor and improved investigation policy as well as the required equal-tools single-agent baseline; ablate retrieval/review policies if feasible. Do not claim improvement from a diagram or agent count.

Compare with one agent using the same tools, records, raw report, clarification rules, and replayed failures. Hold the model constant and document comparable budgets. Measure root-cause accuracy, evidence grounding, total attempted tool calls, end-to-end latency and all-model token usage; separately assess issue discovery and appropriate abstention. Include all monitor/critic calls in token and latency accounting, report their call count separately, and compare with/without local monitoring to test its value. Do not leak target service/time, root-cause labels, or future fixes.

Deliver runnable code/setup, coordination diagram, synthetic dataset/tests, comparison results, a technical note of at most 500 words, and the coding-assistant transcript. No hardcoded incident answers. Document external dependencies and incomplete functionality. These requirements and scenarios are not a claim that an implementation or tests already exist.

## Research basis for the AI evidence layer

Langfuse documents nested traces spanning model calls, retrieval, tools, inputs/outputs, timing and metadata. This supports the choice of observable AI execution evidence; it does not itself supply our diagnosis architecture. [Official tracing documentation](https://langfuse.com/docs/observability/overview)

Its prompt-management documentation links a generation to the prompt version it used, enabling comparisons by version. This supports collecting actual prompt-to-run links rather than inspecting only the current template. [Official prompt-to-trace documentation](https://langfuse.com/docs/prompt-management/features/link-to-traces)

Accessed 20 October 2026. Documentation is live and undated; these sources were inspected, not installed or benchmarked. Proposed requirements, examples, and diagnosis rules are our design analysis.
