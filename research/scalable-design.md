# Large-estate investigation design

Design target: billions of code lines across many repositories, millions of telemetry records, connected services, databases and AI applications. This is a proposed design, not an implemented system or a billion-line performance result. The [visual architecture](architecture.html#large-estate) is the short reading view; this file defines the contracts and limitations.

## 1. The architectural change

Separate **estate preparation and indexed retrieval** from **per-incident agent investigation**. The model never receives the whole estate. Existing agents investigate bounded questions using searchable source systems; they expand their scope when evidence warrants it. Adding context length or one agent per repository does not solve retrieval.

There are three logically different maps:

- **Estate map:** discoverable services, repositories, deployments, APIs, queues, databases and AI workflows. Prepared continuously, incomplete and potentially stale.
- **Incident working map:** only the relevant candidate entities/connections, with evidence and unknowns. Built and revised during investigation.
- **Causal explanation:** which faults explain observed divergence. Neither dependency adjacency nor search relevance establishes causation.

No graph database, vendor or framework is selected. Typed adjacency records and existing search backends may suffice initially. A static code-call index alone cannot establish runtime HTTP/queue routing, configuration-dependent behavior or product intent.

## 2. Prepare before an incident

| Prepared capability | What it contains | Freshness and limitation |
| --- | --- | --- |
| Authorized source/service directory | Feature aliases, owners, namespaces, endpoints, repos, telemetry backends, API/queue/DB/AI workflow references | Source references, last refresh and missing fields; a catalog does not identify the faulty service. |
| Versioned code search/navigation | Repository-qualified text/symbol search; definitions/references where supported; exact revision files; diffs, API/event schemas and dependency manifests | Incremental indexing by repo/revision. Expose unsupported languages, index failures and revisions not indexed; use bounded exact-revision fetch as fallback. |
| Deployment/artifact mapping | Service + environment + instance + active interval → artifact digest → source repos/commits, dependencies, effective config/flags | Many-to-many: one service can use several repositories/artifacts; one repo can deploy several services. Generated code/shared libraries need their own provenance. Missing build bindings remain gaps. |
| Telemetry access | Existing partitioned log/metric/trace/queue/provider stores; low-cardinality routing fields; message/run correlation; retention and sampling metadata | Do not copy every log into agent memory or one vector store. High-cardinality IDs need backend-appropriate fields/metadata, not automatically index labels. |
| Data and AI execution access | Schema/lineage catalogs; bounded read-only record/history queries; prompt/model/retrieval/tool/handoff versions and actual run inputs/outputs | Current DB values or current prompt templates do not reconstruct a past execution. Historical access depends on actual retention/audit capabilities. |
| Searchable operational knowledge | Versioned contracts, tests, runbooks and historical incidents with source and validity metadata | Useful leads and expected behavior, not proof the present cause matches an earlier incident. |

Use change/build/deployment events and incremental refreshes rather than rebuilding every repository at incident start. Retain content-addressed/versioned references according to policy; do not promise unlimited retention or complete indexes. Partition large indexes by appropriate organization/permission/repository/time domains; storage and query engines do the distributed search, not LLM agents scanning shards.

## 3. Start from vague text without an organization-wide raw scan

Only `report_text` is user input. Identity and permitted organization/source scopes are established by the application, outside the model; the model cannot grant itself another tenant's access.

1. D1 searches the authorized directory using feature terms, aliases and semantic matches, yielding a bounded candidate page—not every file or log. Search rankings are provisional. If catalog search is empty, bounded organization-wide **metadata/index** searches can look for endpoint/tool/event identifiers; do not silently scan all raw history.
2. D3 checks inexpensive available summaries for candidate services: error/delivery counters, relevant business outcomes, onset and healthy/affected cohorts. Technical health alone can miss AI-quality and business failures, so D6 run metadata or direct outcome events may be needed.
3. Record initial time/environment assumptions; widen them when evidence is absent or ambiguous. Do not assume a complaint is recent or that one matching error is the user's issue.
4. When several scopes remain plausible, ask for the group, approximate time or example attempt. Useful independent checks may continue within limits. A minimum supported workflow requires configured searchable sources and a valid access scope; arbitrary vague text cannot uniquely identify any incident in the world.

Do not permanently discard low-ranked candidates. Keep a search frontier and query history, including candidates not inspected. Reserve configurable discovery effort for alternative sources/cohorts so an early retrieval mistake does not become the final diagnosis.

### Learn before asking implementation-specific questions

D1 knows the available tools and discovered candidates, not the application's internals. A recorded failure stage enables D4/D6 to explain its actual implementation; those findings establish dependency/read identities and make narrower D5/D3 questions possible. Specialists also return unknowns and suggested follow-ups. Do not infer a cache or database field merely because it is a common engineering pattern. An explicitly exploratory existence question is allowed; an invented concrete resource/failure is not a factual premise. See the [question-grounding contract](question-grounding.md).

Every task records known premises and source references, exploratory assumptions, missing prerequisites, why the question is justified now and what it could distinguish. D1's self-check and D7's independent source/premise review audit the investigation itself. Structural validation checks real references/IDs and limits, not semantic truth; a valid citation can still be irrelevant. At scale the compact state must preserve these distinctions rather than turn provisional summaries into facts. Missing bindings/history trigger discovery or a limited report, not guessed application knowledge.

## 4. Follow only relevant cross-repository boundaries

For a messaging complaint, an illustrative discovered path is:

`AI workflow repo@a7 → message API repo@b2 → queue Q → worker repo@c9 → group-mapping DB → external provider`

The ordering is application-specific; some systems resolve destinations before enqueuing, use an outbox or have no AI entry point. D4 follows endpoint definitions, publish/subscription configuration, schema identities and artifact bindings. D3 corroborates execution with request/job/message IDs, span links and timestamps. D5 checks the data the application actually read, including caches/replicas; D6 follows the actual AI decisions/tools/handoffs. Resolve each service's revision separately; never assume one shared Git SHA.

Expand the incident map along a supported edge or explicit rival hypothesis. Use bounded neighbor pages and cycle detection. A high-fanout database, queue or shared library is not a reason to inspect every consumer: choose affected/healthy cohorts, routes, schemas and activation intervals, retaining unexamined scope. Broaden deliberately if the current branch fails to explain the symptom.

Edges record relation type, source, tenant/environment, validity interval, observed-at time, version and whether declared, statically inferred or runtime-observed. Stale/contradictory edges can coexist pending resolution; do not merge them into a fictional single route. Temporal order needs clock/ingestion uncertainty, not timestamp proximity alone.

## 5. Progressive retrieval rather than evidence dumping

| Source | Narrowing strategy | Evidence sent to agents |
| --- | --- | --- |
| Logs/metrics | Time and source/service/environment filters; counts and groups; relevant error patterns; correlated attempt lookup | Aggregate scope plus a bounded set of source-linked events, including successes/counterexamples. Rare patterns must not vanish behind frequency-only summaries. |
| Code | Service/artifact → relevant repo@revision → endpoint/symbol/schema → callers/consumers → selected files/diffs | Exact code slices with repo, commit, path and symbol/range; not entire repositories. Inspect unchanged code too—no recent commit is required for a bug. |
| DB/data | Entity/run → actual query/read path → primary/cache/replica → time-matched values/history | Minimum necessary rows/fields, query semantics and consistency/coverage limits. Never let an LLM issue an unbounded table dump. |
| AI runs | Workflow → candidate run → decision/tool/retrieval/handoff step → related code/data | Actual prompt/version and relevant inputs/outputs/state deltas, not all prompts across all agents. |
| Changes/history | Related services/config/schema + activation window, then mechanism checks | Relevant candidates and explicit alternatives. Search similarity and timing are retrieval signals, not causal proof. |

Use lexical/exact identifiers, structured filters and code relationships; semantic search can improve feature discovery but cannot replace exact evidence binding. A useful reduction is `search → aggregate → retrieve originals → test claim`. Ranking must retain diversity and expose omitted/partial scope. A model ranker cannot recover a cause that retrieval never supplies.

Every query must bound time, rows/bytes, duration and backend work where supported. A small response limit alone does not bound scanning cost. Use adapter-specific query planning, allowed query templates or validated parameters; disallow unlimited wildcards/scans. Split approved broad work into cancellable bounded partitions; reject or defer it if the backend cannot safely enforce limits.

## 6. Agent responsibilities at scale

No new permanent agent is needed for each service or index.

- **D1:** reasoning plus orchestration: maintains competing explanations, combines cross-source findings, chooses distinguishing tests, owns scope/frontier, selected tasks, priorities, progress and stopping. Holds compact state and source references, not all raw evidence or every specialist conversation. The separate analyst is removed; D2 is a retired ID, not an available agent.
- **D3–D6:** bounded local investigation; choose relevant queries, inspect originals, produce observations/counterevidence/gaps and flag unexpected leads. Several task invocations can pursue independent branches, within a shared cap—not an unbounded swarm per service.
- **D7:** challenge the leading causal mechanism and ignored scope, with authorized access to source originals and ability to request a rival test outside D1's chosen branch. Separate context does not guarantee different model bias.
- **D8:** write from scoped reviewed claims, including expected/observed path, failure point, supported causes/contributors, alternatives, actions and gaps. Every material claim references evidence, not merely another agent's prose.

The case file holds versioned findings, evidence references, query results/statuses, frontier/visited entities, task dependencies and budgets. Keep evidence snapshots immutable where retained; allow interpretations to be superseded and reconsider dependent conclusions. Source originals are fetched on demand. Context compression retains contradictions, scope and unknowns; a summary never upgrades an uncertain observation to fact.

All seven [individual contracts](agents/README.md) share the [agent protocol](agent-protocol.md). Late results carry scope/dependency versions and undergo applicability checks before atomic state updates; do not discard useful independent evidence merely because the global case revision changed. Duplicate deliveries are idempotently ingested. Final approval binds report bytes and relevant dependency versions, is invalidated by material changes, and is checked again at delivery. A reviewer outage or exhausted budget without valid approval yields deterministic `investigation_incomplete` status, not an unreviewed causal narrative. A reviewed inconclusive report is a different, valid outcome.

## 7. Bounded tool contracts

The payloads in this section illustrate retrieval semantics. The exact current per-operation arguments, data fields, eligible agents and schemas are in the [tool catalog](tool-catalog.md) and [contract files](contracts/README.md). [Runtime placement](runtime-and-tools.md) explains how connectors query code hosts, approved replicas, deployment APIs and actual cloud/log stores. The LLM chooses calls; backend code executes them.

All source adapters implement equivalent semantics, not necessarily one physical search engine. Example request:

```json
{
  "question": "Did the selected worker resolve a destination for M17?",
  "scope": {
    "service": "delivery-worker",
    "environment": "production",
    "event_time": ["2026-10-20T10:25:00Z", "2026-10-20T10:40:00Z"],
    "message_id": "M17"
  },
  "source_snapshot": "adapter-specific-snapshot-or-live",
  "limit": 50,
  "timeout_ms": 5000,
  "cursor": null
}
```

Service/time/message identifiers are discovery outputs, not hidden input hints. Example values/limits are illustrative, not tuned defaults. Trusted authorization context is attached outside this model-controlled body and enforced for search, metadata, fetch and cache lookup.

Responses include:

```json
{
  "status": "partial",
  "items": [],
  "evidence_refs": [],
  "coverage": {
    "searched_scope": "recorded validated scope",
    "complete_for_requested_scope": false,
    "partial_reasons": ["one partition timed out"],
    "sampling": "source-reported-or-unknown",
    "retention": "source-reported-or-unknown",
    "index_watermark": "source-reported-or-unknown"
  },
  "next_cursor": null,
  "cost": {"elapsed_ms": 5000, "bytes_scanned": null},
  "source_snapshot": "adapter-specific-snapshot-or-live"
}
```

Empty `items` with `partial` is not a negative finding. Even a complete query establishes absence only within its recorded source, query semantics, instrumentation and time scope. Represent denied/timeout/error separately from empty success. Counts may be approximate/lower-bound; adapters must label that.

Use stable ordering/cursors and bounded pages, with a backend snapshot where available. A pagination snapshot stabilizes a current query; it does **not** reconstruct an old DB state or historical index. Preserve both event time and ingestion/query availability; late evidence may reopen a finding.

## 8. Search expansion and failure behavior

| Challenge | Required response |
| --- | --- |
| True service is not in the first candidate page | D1 can broaden its hypothesis/search; D7 can request another page, alternate feature/endpoint terms, neighbor expansion or an uninspected cohort. Report retrieval scope; do not equate top-k with all possibilities. |
| Catalog/code index is stale or exact revision absent | Refresh or fetch a bounded exact-revision slice when authorized; retain the deployed binding gap if unavailable. Do not substitute latest branch code silently. |
| Missing distributed trace IDs | Correlate message/job/entity IDs, queue records, source-defined links and time with explicit uncertainty. Timestamp proximity alone is insufficient; no unique match means ambiguous. |
| Error storm millions of lines long | Backend aggregations and pattern representatives plus controlled rare-event/counterexample retrieval; original evidence remains queryable. Deduplication must preserve counts/time coverage and rare initiating events. |
| Shared dependency affects many services | Compare cohorts and expand likely propagation paths; allow multiple causal chains. Do not force one fault or traverse every neighbor. |
| Source unavailable, sampled or outside retention | Preserve partial findings, try an independent source when useful, then stop with gaps. Do not retry until a critic agrees. |
| Backend slow/overloaded, many incidents at once | Per-source/tenant concurrency and rate/scan limits, backpressure/cancellation and bounded retries; fail safely instead of overloading production. Retries consume global budgets. |
| Conflicting versions/evidence or delayed arrivals | Retain source versions and revise the incident map/findings. Revalidate caches and reopen conclusions; do not silently overwrite the record. |

Global limits apply across all roles, retries and parallel branches: wall time, query/scan cost, model tokens, task count and concurrent backend work. Unchanged stateless queries require a reason to repeat. When no new information arrives, switch source/scope, clarify, or return an explicit limited result. Cache keys include authorization scope, query, source revision/snapshot and time; mutable live data has freshness bounds and invalidation. Shared caches must never leak cross-tenant evidence.

## 9. Example: crossing repositories without reading them all

All details below are hypothetical, not measured counts or an incident solution implemented in code.

1. User: “Messages aren't reaching the customer group.” Authorized directory search returns candidate messaging workflows. D1 records candidate scope; ambiguity may require clarification.
2. D3 retrieves delivery-outcome aggregates and identifies a candidate failed attempt, M17. D4 looks up only candidate service-to-repo/deployment mappings, not every repository.
3. Runtime links connect API job creation, queue Q and a worker attempt. D4 independently resolves the API's repo@b2 and worker's repo@c9. D6 inspects the AI send decision only if that upstream step is implicated.
4. An explicit worker outcome localizes recipient-resolution failure. D1 first asks D4 to explain that stage's relevant deployed implementation, input/read source and failure branches. After D4 identifies them, D1 can ask D5 about the established mapping/read scope and historical values. D3 can independently corroborate actual execution. Do not ask about an undiscovered field or invent a cache.
5. If a schema producer/migration belongs to another repository, the schema identity and migration/deployment records justify that next expansion. The culprit need not be in the alerting service or in a recent code change.
6. D1 compares missing-data versus incompatible-consumer explanations as part of its own reasoning. D7 asks for historical values/actual deployed binding, and challenges whether another uninspected cohort contradicts the conclusion.
7. D8 reports the supported path and causal mechanism for the inspected scope, with direct evidence and broader-impact gaps. No one claims that all organizational code/logs were examined or that a provider acknowledgement establishes customer visibility.

## 10. Security and evidence boundaries

Read-only does not mean cost-free: enforce backend resource limits and tenant-scoped least privilege. Filter authorization before ranking where supported and recheck every fetch; embeddings, metadata, snippets and caches are also sensitive. Redact PII/secrets and inspect effective config differences without exposing secret values. Treat source content as untrusted data, not instructions; validate tool parameters and permissions outside the LLM. Do not permit shell/SQL/deployment mutations or unbounded experiments merely to verify a theory. Keep application-agent failures and investigator failures distinguishable in audit traces.

## 11. What must be demonstrated, not asserted

The assignment prototype can use multiple small versioned repos and simulated source adapters while preserving these contracts. That is not evidence it handles a billion real code lines. Avoid deploying a full search platform merely to make the diagram look production-ready; integrate appropriate existing indexes through adapters when available.

Test increasing distractor volumes and repository/service counts with held-out incident variants. Suggested staged workloads: 10/100/1,000 repository metadata entries and 10,000/100,000/1,000,000 telemetry records, with separately reported indexed code volume. These are workload plans, not results; metadata entries are not equivalent to fully indexed repositories. A credible billion-line claim requires representative real index/storage/build/deployment workloads and sustained ingestion, not extrapolating from this synthetic test.

Measure relevant-source/cause retrieval recall before reasoning; candidate recall after expansion; boundary localization; root-cause and multi-cause accuracy; grounding/abstention; all-model tokens; backend bytes/rows scanned; latency percentiles; indexing lag; storage/indexing cost; concurrency and tenant-isolation behavior. Report infrastructure/index work separately from LLM cost. The baseline uses the same search/access/retrieval capabilities, not raw-data overload, so comparisons test coordination fairly.

Stress stale mappings, missing revisions, broken traces, delayed ingestion, graph cycles, high fanout, rare initiating events hidden in noise, misleading unrelated deployments, old-code faults, provider acceptance without delivery, and tool timeouts. Place some true causes outside the first retrieved page and some outside the alerted service. Test a deliberately inconclusive case and an unauthorized tenant. Compare the basic supervisor and this policy; only claim benefit if measured.

Also inject failures of the investigator's own reasoning: a plausible invented cache, wrong-field question before code discovery, real but irrelevant citations, omitted history/deployment prerequisites and partial-query summary drift. Test whether the system detects/reframes them without user correction; report escape rates instead of asserting that a critic always catches them.

## 12. Primary sources and what they actually establish

Accessed 20 October 2026. Our cross-repository pipeline and contracts are a synthesis; no source proves the complete proposed architecture or its billion-line performance.

- [Meta: AI-assisted incident response](https://engineering.fb.com/2024/06/24/data-infrastructure/leveraging-ai-for-efficient-incident-response/): ownership/runtime-aware retrieval narrows changes before model ranking. Its study concerns a web monorepo and change candidates, not our multi-repo system or all incident classes.
- [Sourcegraph: precise code navigation](https://sourcegraph.com/docs/code-navigation/precise-code-navigation): repository indexes and language-specific SCIP navigation, with search fallback. This supports symbol retrieval, not complete dynamic service causality.
- [Backstage: catalog descriptors](https://backstage.io/docs/features/software-catalog/descriptor-format/): components, owners, APIs/resources and dependency declarations. These are declared metadata, not automatically verified runtime truth.
- [Grafana Loki: query best practices](https://grafana.com/docs/loki/latest/query/bp-query/): narrow time/source filters early and use backend-efficient queries/aggregations. This does not guarantee a fixed latency or require Loki as our backend.
- [Elasticsearch: pagination](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results): deep-offset costs, cursor-style search-after and point-in-time query consistency. A PIT is not historical-state reconstruction.
- [OpenTelemetry: messaging spans](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/) and [sampling](https://opentelemetry.io/docs/concepts/sampling/): producer/consumer context links and sampling trade-offs. Missing instrumentation cannot establish nonexecution.
- [SLSA provenance](https://slsa.dev/spec/v1.1/provenance): artifact/build/input provenance structure. Availability and trust depend on what an organization actually records/verifies; it does not itself supply effective runtime config or every service-to-source binding.
- [Resolve engineering retrospective](https://resolve.ai/blog/Failures-That-Led-to-2x-Agent-Accuracy-Improvement): focused investigators, structural verification and shared evidence; motivates bounded agent contexts, not a measured result for our design.
- [incident.io engineering account](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre): revisable cited findings and time-frozen evaluation. Helps define evidence lifecycle and honest testing.
