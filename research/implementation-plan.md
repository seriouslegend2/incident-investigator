# Implementation plan — incident investigation system

**Decision:** implement one durable investigation control plane with seven *logical* LLM roles and a separate policy-enforcing tool gateway. It is not seven VMs, an all-access process, or an LLM with database/cloud credentials. The model chooses a permitted next operation; trusted backend code validates and performs it.

This is a build plan, not a claim that the integrations, replica, indexes, IAM identities or benchmark already exist. It is based on a read-only review of the KookarCore checkout named by the team. Source facts and recommendations are labelled below.

## Implementation decision record (updated)

The implementation is a real demo application, not a fixture-only workflow visualisation:

- Each of **D1, D3, D4, D5, D6, D7 and D8** gets its own KookarCore-style package: prompt seed, Pydantic request/result contracts, restricted tool wrapper(s), executor/build definition and tests. D2 remains absent.
- The LangGraph workflow calls actual OpenAI model turns with structured tool calls. It must not encode a fixture's final diagnosis in code or let the model simply repeat one.
- Demo evidence is seeded but real: sample logs/traces, deployment/config records, code-index records, database/history records and AI-run records. Tools query those sources and return bounded, cited evidence.
- Postgres/Supabase persists cases, task invocations, tool calls, evidence receipts, claims and report revisions. LangSmith receives actual LLM/tool execution traces correlated by case and task identifiers.
- API keys and connection strings are runtime configuration only. They are never committed, embedded in prompts or placed in documentation.
- The initial demo does not connect to live AWS/Azure/GCP or production databases. A later live connector follows the gateway/source-catalogue design in this plan; it is not simulated by broad credentials.

The previous fixture-only prototype is intentionally discarded before this implementation starts.

## 1. What we are building

An operator supplies a vague complaint such as “customers in group A did not get a message.” The system will:

1. Create a durable case, preserve the original wording, scope and clock.
2. Discover candidate services and expected workflow boundaries rather than assuming a table, repository or log group.
3. Request only the specialist checks needed to locate the first unexplained boundary.
4. Store every query result as cited, bounded evidence with source/revision/time/coverage.
5. Compare expected implementation with observed execution and data/AI behavior.
6. Return a reviewed incident report: observed flow, expected flow, supported cause or unresolved alternatives, counterevidence, affected scope, gaps and proposed (never automatic) next actions.

The seven logical roles are **D1, D3, D4, D5, D6, D7 and D8**. There is deliberately **no D2**. D1 owns reasoning and dynamic orchestration; D7 is an independent evidence critic. This is our design choice, not a claim that the assignment’s example agent list must be copied.

## 2. Source review: what KookarCore already provides

### Reusable execution patterns — source facts

| Existing source | What it establishes | How we use the idea |
| --- | --- | --- |
| apps/kookarcore/app/eda2/envelope.py and directory.py | Typed invocation requests and a generated Worker/local placement directory. | Give every specialist task a case ID, scope version, correlation keys, time budget and structured result contract. |
| app/eda2/dispatcher.py | Deduplication, latest-wins supersession, result handling and workflow continuation. | Preserve duplicate/superseded task rules; add a separate durable case ledger rather than treating queue state as evidence. |
| apps/kookar-workers/src/runtime/agent-factory.ts | A shared LangChain worker chassis: context, role middleware, model/prompt selection and structured-output repair. | Reuse the factory pattern for role prompts, local output validation and run tracing. |
| apps/kookar-workers/src/queue/consumer.ts, callback.ts, runs.ts | Asynchronous queue work, callback, redelivery protection and DLQ bridge. | Reuse the asynchronous task shape; make case/evidence writes authoritative and idempotent. |
| app/services/eda/cf_dispatch_service.py | Oversized state by reference and callback context stored before enqueue. | Send small task references, never whole repositories, large log sets or DB result dumps through an LLM queue message. |
| Worker house-log middleware and request-scoped LangSmith tracing | Run logging/tracing exists. | Add explicit case/task/correlation propagation and investigator run/tool/evidence/report lineage; do not mistake a trace for source evidence. |

### Important limits — source facts

- The current KookarCore/Supabase client is application-capable: generic helpers and service-role configuration exist. It must **not** be reused as D5’s investigator credential.
- Existing queue run bookkeeping is explicitly best-effort. It cannot be the authoritative incident/evidence store.
- Existing EDA2 deduplication, scope tokens and workflow/callback state have finite TTLs. They cannot be the long-lived investigation authority, and a failed callback must be recoverable rather than merely retried.
- Current Workers can safely run the LLM loop, but a Worker should not be granted direct unrestricted access to private databases, cloud accounts or secrets.
- Checked-in prompts can be seed/fallbacks while remote prompt management is runtime truth. Investigation must record the exact prompt/model configuration actually observed, not infer it from a repository file.

## 3. Recommended physical topology

    operator / API / UI
              |
              v
    Investigation control plane
    Case API · scheduler · policy · durable case/evidence/report store
              |
              +------------------------+
              |                        |
              v                        v
    LLM role runner                 work queue
    D1/D3/D4/D5/D6/D7/D8       idempotent + DLQ
              |
              | approved tool request only
              v
    Private evidence gateway
    policy · redaction · audit · pagination · typed adapters
              |
              +-------+-----------+-------------+-------------+
              v       v           v             v
            Git host  DB replica  cloud/logs    AI traces/
            + code    / history   deploy/config prompts/retrieval

**Control plane:** an operator-facing, authenticated API, scheduler, case store and delivery guard. It may be implemented beside KookarCore’s EDA2 workflow engine. Choose its ingress explicitly; the inspected Core ACA deployment is internal/private, not evidence that this API should be public.

**LLM runner:** one logical worker/runtime can host all seven roles. Kookar’s Cloudflare Worker factory/queue approach is a good fit for asynchronous task execution. It must receive task inputs, allowed tool schemas and redacted tool results—not credentials or network-wide access. Deploy it as a **dedicated incident Worker service** with its own minimal secret bundle, queue/DLQ and service identities. Putting incident agent folders into the existing Worker bundle does not create per-agent secret isolation.

**Private evidence gateway:** a new small service in the organisation’s private network/VPC/VNet (for example, ECS/Fargate, EKS, VM or equivalent). It contains cloud SDK/API clients, Git host client, replica connection pools, connector policies and audit logging. It is the only component that can reach private sources.

**Runner-to-gateway bridge is a required deployment decision, not an arrow in the diagram.** Either run the role runner inside the same private network, or publish the gateway only through an authenticated private ingress/Tunnel/Access route. For the latter, require both an edge service-token check and a separate application-level audience/scope token (plus mTLS where feasible), an egress allowlist, and source-target allowlisting. Test the positive path and denial for unauthenticated/wrong-identity callers. Never expose the replica or cloud control plane directly to a public Worker.

**Storage:** use a durable transactional database/object store for cases, receipts and immutable reports. Do not rely only on Redis, an LLM trace product or a queue cache. Encrypt it, apply retention and use object storage for large redacted evidence pages.

## 4. Exact source connections

| Need | Where actual data remains | Gateway adapter must do | Never do |
| --- | --- | --- | --- |
| Code | GitHub/GitLab/Bitbucket or a read-only mirrored checkout and a revision-aware code index. | Resolve source ID; search index; fetch bounded path/range at an exact commit; return index freshness and repository revision. | Put all repos in the prompt; use “latest” as deployed revision; execute repository scripts. |
| DB data | An approved read replica and, separately, an approved audit/CDC/history source. | Resolve the case-authorised source scope and per-source mapping; issue parameterized, bounded read templates; return replica lag/observation time. | Use app service-role key, primary fallback, arbitrary SQL/RPC, writes, DDL, callable functions or secret values. |
| Logs / metrics / traces | Configured AWS, Azure, GCP, Datadog, OpenTelemetry or another actual telemetry backend. | Resolve configured account/project/region; make bounded time/query calls; preserve query coverage, sampling/retention and correlation IDs. | Guess a log group, turn “not found” into “did not happen,” or query every account. |
| Deployments / config | CI/CD, deployment platform, container registry, IaC state and config metadata. | Bind running service/instance to image/build/commit; show effective nonsecret config metadata and version/hash diffs. | Reveal secret values, mutate rollout, run rollback/retry, or infer a deployment from a Git commit alone. |
| AI behavior | LLM/agent tracing, prompt registry, retrieval store and application audit events. | Fetch actual run/prompt/model/retrieval/tool/handoff records by correlation/time; distinguish retention gaps from absence. | Treat a checked-in prompt as live truth; resend sensitive transcripts without minimisation. |

### AWS, Azure and GCP

Implement a provider-neutral adapter interface first. Add an AWS adapter only when a registered source belongs to AWS: CloudWatch Logs/metrics/traces, ECS/EKS/Lambda metadata, CloudTrail/CI-CD deployment provenance, Parameter Store/AppConfig **metadata only**, and Secrets Manager **version/rotation metadata only**. Use equivalent configured adapters for Azure/GCP. The system does not need all cloud permissions; it needs narrowly scoped read APIs for each registered source.

Each adapter has its own workload identity. The gateway obtains short-lived credentials from the platform identity mechanism; it does not place cloud access keys in an LLM message, case record or frontend.

## 5. Organisation onboarding before incidents

### 5.1 Source catalogue

Create an operator-managed catalogue, not LLM memory:

| Catalogue entity | Required fields |
| --- | --- |
| Service | service ID, owner/on-call, environment, tenant model, run-time locations, dependencies, correlation fields, SLOs |
| Repository | repo ID, host, default branch, indexed languages, index freshness, deployable component mappings |
| Deployment binding | service/environment/region/instance selector, build/image identifier, commit/manifest/IaC links |
| Data source | DB identity, **replica** endpoint/region, allowed views/tables/columns, per-source scope mapping (including aliases/composite keys), classification, history source/retention/completeness, maximum query limits |
| Telemetry source | provider/account/project/region, permitted query templates, retention/sampling, permitted log/trace/metric datasets |
| AI source | trace/prompt/retrieval/tool/state stores, retention, redaction/classification policy |
| Connector policy | adapter identity, audience, allowed operations, rate/row/scan/time limits, owners and freshness health |

Do not manually enter the whole dependency graph as truth. Bootstrap it from deployment/IaC/service catalog, then continuously verify its bindings and mark unknown edges.

### 5.2 Code and deployment index

1. Install a read-only GitHub App (or equivalent) scoped to approved repositories.
2. Build an async repository synchroniser: webhook/poll → immutable commit fetch → parser/symbol/reference index → service/deploy binding extraction.
3. Keep an exact-revision content store or on-demand bounded fetch service. For billion-line estates, index first; only read a cited file range after search narrows it.
4. Ingest CI/CD and deployment provenance: artifact/image digest, manifest revision, rollout time, environment/region/instance labels.
5. Publish index freshness, unindexed repositories/languages and missing deployment mappings as visible coverage gaps.

### 5.3 Read-replica data connector

Create IncidentReadRepository, entirely separate from KookarCore’s generic write-capable Supabase client:

1. Provision a dedicated database login with TLS, CONNECT, USAGE and SELECT only on approved views/tables; no ownership, BYPASSRLS, DML, DDL, temp-object/large-object privilege, callable functions/RPC or primary endpoint. Revoke EXECUTE from PUBLIC and the investigator role for non-approved functions, and set/verify default privileges for future functions.
2. Use curated incident views where raw data has sensitive message/user payloads. At case creation, map the authenticated operator to an immutable authorised source scope. Gateway maps that scope to each source’s actual tenant/house/composite predicate; an unresolved mapping fails closed. Agent tool arguments never choose another tenant.
3. Network-restrict the connector to the replica endpoint and prevent primary DNS/credential fallback. Start every request in a read-only transaction; set statement, lock, result, scan and page limits; use parameterized templates only.
4. Put a query policy compiler before the driver. It validates a named template and typed filter fields, injects the case-authorised source scope and environment predicates, and rejects broad/paged-out/unsafe requests.
5. Capture connector receipt fields: connection ID (not DSN), replica observation time/lag, template version, relation, allowed columns, row count, continuation state, redaction summary and error class.
6. Use a separate audit/history connector for incident-time state. Define its event-time semantics, retention window, ordering/lag, delete/tombstone treatment and snapshot completeness. Only a source that documents coverage for the claimed interval can support an historic claim; a current replica cannot answer “what was the value last Tuesday?” by itself.

KookarCore’s local migrations show broad service-role access in parts of the current application. Verify deployed grants/RLS with the database owner; the plan must not assume that source policies are suitable for an investigator.

### 5.4 Cloud, logs, deploy and configuration connectors

1. Create a read-only workload identity per provider/source group. Grant only the named resource paths needed by registered adapters.
2. Build bounded query templates for logs/traces/metrics: target service, environment, interval, correlation keys, limit and paging. Record query timeout, retention/sampling and searched interval.
3. Build deployment provenance queries: service instance → deployment ID → artifact digest/build → revision/config manifest. A code commit is evidence only after this binding.
4. Expose configuration as effective nonsecret metadata: name, source, version/hash, last change, scope and presence. Redact values and tell the report when a secret/effective value was intentionally inaccessible.
5. Validate any webhook/deploy event at ingestion; it updates a catalogue lead, not a causal conclusion.

### 5.5 AI application connector

For each AI workflow register model provider, trace project, prompt registry, retrieval indexes/vector stores, tool audit store, handoff/state store and retention policy. The D6 adapter reads:

- exact run/trace and timing;
- rendered prompt or versioned prompt reference;
- model/provider/settings actually recorded;
- retrieval query, document IDs/scores/filter and returned context;
- tool calls/results and parent/child handoffs;
- state/checkpoint versions and failures.

Prompt/model/retrieval evidence can be sensitive. Redact/minimise before returning to a role runner and retain access decisions in receipts.

## 6. Runtime components and ownership

| Component | Owns | Must guarantee |
| --- | --- | --- |
| Case API | create/read case; original complaint; user clarifications; access control | Case ID, immutable operator-authorised source scope + scope revision, tenant/environment separation and original input |
| Case state machine | status and scope revisions | new → triaging → gathering → analysing → drafting → reviewing → delivered or explicit incomplete/cancelled; no silent state jump |
| Scheduler / D1 runtime | task graph, budgets, eligible role selection, cancellation | Dynamic bounded dispatch; no mandatory all-agent fan-out |
| Agent runner | LLM call and output-schema validation | Role gets only task, compact case state, allowed tool names and redacted result pages |
| Tool broker | tool schema validation, policy/limits, receipt persistence | LLM cannot choose an endpoint/credential/tenant outside policy; trusted case scope is injected, not accepted from tool arguments |
| Private gateway | typed source adapter calls | Identity, least privilege, time/row/scan/rate caps, redaction and audit |
| Evidence store | original/redacted pages, append-only evidence receipt, citation metadata | Evidence ID, source/version/query coverage, integrity hash, retention/classification |
| Callback inbox + workflow outbox | accepted task results and transactional follow-up effects | Stable task/result IDs, idempotent result acceptance and recovery after a crash between receipt, evidence write, event and workflow advancement |
| Claim graph | observation / interpretation / assumption / unknown / alternative | Every causal claim cites evidence; contradiction and scope are explicit |
| Review + delivery guard | D7 review and D8 draft delivery | Approval binds exact report bytes + dependency versions; a changed report/evidence invalidates it |
| Audit/operations | investigator activity, failures, costs, health | No secrets/PII in logs; append-only application audit records. Add independent WORM retention or externally verifiable hash anchoring before claiming tamper-resistant audit. |

### Minimum durable records

cases, case_scope_revisions, tasks, task_attempts, callback_inbox, workflow_outbox, tool_calls, tool_receipts, evidence_objects, claim_nodes, claim_edges, read_contracts, source_catalogue, connector_health, reviews, reports, report_dependencies, delivery_attempts, audit_events, evaluation_runs.

Store immutable IDs/hashes and state transitions. Large evidence belongs in encrypted object storage referenced by a receipt; do not use an LLM transcript as the system of record. Use durable idempotency records independent of current EDA2 Redis/queue TTLs. A remote-enqueue timeout is ambiguous: reconcile task acceptance by stable task ID before any fallback or make all effects idempotent; do not blindly rerun it locally.

## 7. Roles, tools and handoffs

| Role | Initial input | What it may ask through tools | Output / cannot do |
| --- | --- | --- | --- |
| D1 investigation lead | vague complaint, case scope, source catalogue discovery access, prior evidence summaries | find sources/history; create bounded specialist tasks; compare alternatives and choose discriminating checks | task graph + claim updates; cannot invent architecture/tables or call raw cloud/DB |
| D3 observability | target boundary/service/time/correlation candidates | logs, metrics, traces, message/provider status and correlation operations | observed execution/coverage gaps; cannot infer source code/data cause |
| D4 code/deployment/infra | expected boundary or source discovery task | code index/read/references, build/deploy/config/infra tools | implementation/deploy facts + ReadContract; cannot query production data directly |
| D5 data | cited ReadContract or candidate schema + entity/time | replica metadata, bounded record/history/lineage/cache diagnostics | data facts/consistency; cannot use app client, write or assume a table is used |
| D6 AI behavior | workflow/run/correlation or discovered AI boundary | prompt/model/retrieval/tool/handoff/state traces | actual AI behavior and gaps; cannot infer live prompt from source alone |
| D7 critic | exact evidence/claims/draft and a specific premise to test | independent bounded source rechecks | accept/reject/revise gate and counterevidence; not a second dispatch orchestra |
| D8 writer | approved/cited claim graph and report template | evidence references and draft store only | grounded report draft; never approves itself or investigates new facts |

The exact input/output schemas, examples and 41 tool definitions already live in contracts/agent-io.schema.json, contracts/tool-contracts.json, tool-catalog.md and the seven agents/*.md files. Reuse them as source-controlled contracts. A provider adapter maps the contract to the model provider’s tool/structured-output mechanism and then validates returned JSON locally.

### Critical D4 → D5 data handoff

D4 does not merely tell D5 “check the DB.” It produces a cited ReadContract:

repository + exact revision + file/range → connection binding → relation/view → lookup keys/predicates → selected fields → transform → failure branches → unknown environment binding

D1 gives this plus case entity/time to D5. D5 verifies it against the authorised replica schema and then executes the smallest permitted read. If D5 finds only candidate tables, it reports that uncertainty; D4 must verify the application link. This is how a specialist DB agent can search safely without being given every codebase or guessing tables.

## 8. End-to-end execution

1. **Create case.** API validates operator identity/scope and stores raw complaint. It binds the operator-authorised source scope immutably to the case/scope revision. Runtime assigns case ID and records its current clock. No source access is assumed.
2. **Discover.** D1 calls catalogue/history discovery. It creates a workflow boundary map such as intent → record → enqueue → consumer → destination resolution → provider accept → callback/delivery → customer-visible.
3. **Locate the first unexplained boundary.** D1 invokes only relevant specialists. Example: D3 for observed attempts; D4 for code/deployed revision; D6 when an AI handoff is involved. Independent checks may run in parallel only when they share no prerequisite.
4. **Gather safely.** A role requests a declared tool. Broker validates task/role/schema/scope; gateway resolves the opaque configured source ID, applies access/redaction/bounds, runs the query and persists receipt/evidence. The model gets a small result page plus cited IDs.
5. **Compare explanations.** D1 maintains alternatives and asks a discriminating question before causal promotion. Example: “queue stalled” and “recipient data missing” predict different execution/data observations.
6. **Cross-domain binding.** D4 verifies code/deploy/config; D5 checks the cited data path; D3/D6 establish observed behavior. Time, tenant, environment, region and deployed version must match.
7. **Review and write.** D8 drafts only from stored claims. D7 independently checks exact cited originals, alternatives, contradictions, scope and unsupported certainty. A D7 failure or budget exhaustion yields investigation_incomplete, not approval.
8. **Deliver safely.** Delivery guard hashes the exact report and dependencies again. If relevant evidence or draft changed, return to D1/D7; do not silently send stale text. The report proposes actions; it never runs remediation.

### Concrete message failure example

Complaint: “Customer group A did not receive the reminder.”

1. D1 catalogue search finds a messaging service and uses D3 to search a bounded recent interval. D3 returns a cited attempt ID and finds a destination-resolution error before provider submission.
2. D1 asks D4 to locate the deployed resolver. D4 binds the running deployment to an artifact/commit, reads the resolver path and returns ReadContract RC-17: a lookup of group destination fields, plus uncertainty about the environment connection mapping.
3. D7 checks that RC-17 actually cites the deployed revision and says whether its premises are sufficient.
4. D1 asks D5 with RC-17, group A and time. D5 verifies schema/replica binding and returns: the required destination row was absent at the current replica state; historic state is unavailable. This is **not yet** proof it was absent at incident time.
5. D1 requests an audit-history check or states the temporal gap. If history shows deletion before the event and D3 shows resolution failure, the report can support the missing-data cause. If history is missing, report a supported current inconsistency plus unresolved incident-time state, not a definitive root cause.

## 9. Security, privacy and safety gates

- Separate identities for API, dedicated incident Worker, incident queue/DLQ, gateway, each cloud adapter and each replica. Prefer short-lived workload identity and mTLS/OIDC service-to-service authentication.
- Broker enforces role/tool/source/tenant/environment policy on every call; trusted case scope is injected and verified against the operator authorisation. LLM-provided arguments never widen permissions or select a tenant.
- No generic shell, arbitrary URL fetch, arbitrary SQL, raw secret/config-value tool, deployment mutation, replay, message send or automatic remediation tool.
- Redact/minimise PII and secrets before model context; mark withheld fields/coverage. Treat repository text, logs and retrieved data as untrusted evidence, never tool instructions.
- Encrypt data in transit/at rest; define regional/data residency, retention, deletion/legal-hold and access-review policies with security/legal owners.
- Audit operator, runtime, connector and delivery actions. Store query shape/receipt, not credentials or raw sensitive bind values. Treat database audit rows as application append-only records unless access/recovery policy plus WORM/hash anchoring has been operationally proven.
- Rate/row/scan/token/concurrency budgets apply at gateway and scheduler. Source error, empty response, sampling/retention gap, denial, timeout and model/schema error remain different states.

## 10. Implementation sequence and acceptance gates

| Phase | Build | Exit gate |
| --- | --- | --- |
| 0. Decisions | Select first service/environment, cloud/source platforms, data classification, delivery audience, retention and human-owner model. | Written source catalogue for one pilot; security sign-off on boundaries. |
| 1. Foundations | Case DB/state machine, evidence/receipt/claim schema, operator API, audit logging, redaction library, policy engine. | API cannot cross tenant/environment; evidence IDs/hashes and state transitions pass tests. |
| 2. Safe gateway | Private gateway deployment, chosen Worker-to-gateway bridge, OIDC/mTLS, connector registry and health checks; Git index + one telemetry/deploy adapter. | Positive private-path test succeeds; unauthenticated/wrong-identity callers, broad/external/unregistered queries and secret leaks are rejected. |
| 3. Data path | Dedicated replica role, curated views, history connector, template compiler and query receipt. | Integration test proves SELECT succeeds while insert/update/delete/DDL/RPC/function execution and every primary/DNS fallback fail; timeout/row caps prove enforced. |
| 4. Runtime roles | Dedicated incident Worker/queue/DLQ, D1/D3/D4/D5, task protocol, broker, durable inbox/outbox, compact context and structured validation. | Synthetic incidents dynamically invoke only needed roles; duplicate/superseded/cancelled outcomes and ambiguous enqueue/callback crashes are recovered safely. |
| 5. AI + review | D6, D7, D8; report template, dependency-bound review and delivery guard. | D7 contradiction blocks delivery; changed draft/evidence invalidates approval; review outage returns incomplete. |
| 6. Kookar integration | EDA2 transforms/workflow, generated Worker registry/placement, callback correlation and source catalog integration; add disable-new-investigations and disable-tool-calls switches plus degraded/rollback behavior. | Offline workflow + queue callback/DLQ tests and post-deploy private-path synthetic checks (runner↔gateway auth + harmless connector) pass; Kookar deploy/revision binding appears in citations. |
| 7. Evaluation / pilot | Holdout incident corpus, same-tools single-agent baseline, shadow mode, operator feedback, cost/latency/safety metrics. | Meets pre-agreed grounding/localisation/safe-abstention thresholds before wider rollout. |

### File-level proposed implementation map

| Repository area | New implementation responsibility |
| --- | --- |
| apps/kookarcore/app/incident_investigation/ | case API, state machine, claim/evidence repositories, policy decisions and report delivery guard |
| apps/kookarcore/app/eda2/workflows/ and transforms/ | case lifecycle / task callback transforms; Core may coordinate, but persistent case authority is the new durable case store, not existing Redis workflow TTL state |
| new dedicated incident Worker service/config | seven role definitions/prompts/output schemas, separate minimal secrets, isolated queue/DLQ and service identity; no cloud/DB credentials |
| apps/kookar-workers/src/runtime/ | strict provider adapter, case/task context propagation and typed tool-call bridge |
| new services/incident-evidence-gateway/ | private connector policy, Git/code index client, replica/history clients, cloud/log/deploy/config and AI-trace adapters |
| infra/ | private networking, workload identities, secret references, queue/DLQ, monitoring, dashboards and alert policies |
| supabase/migrations/ or an isolated investigator database | case/evidence schema. Prefer an isolated DB/schema and dedicated roles; do not piggyback application service-role permissions. |
| tests/incident_investigation/, worker tests, gateway contract tests | fixture-only integration tests, security-negative tests, replay/DLQ and evaluation harness |

This map is a proposal. The actual file locations should be confirmed when implementation is authorised; no repository files or production systems were changed for this plan.

## 11. Test and operations plan

### Automated tests

- Contract: every tool request/result validates; malformed model output fails closed after bounded repair.
- Connector policy: unregistered source, unauthorised case scope/alias mapping, broad interval, arbitrary SQL, write verb, function/RPC call, primary endpoint/DNS fallback, secret field and prompt-injection-shaped content are rejected/redacted.
- Data: read-only role/transaction/network, revoked EXECUTE/default privileges, RLS or scope-filtered views, query cap/timeout, history completeness/retention/event-time semantics versus current-replica semantics, and stale/lag disclosure.
- Workflow: stable task ID, ambiguous enqueue reconciliation, callback inbox/outbox crash recovery, idempotent effect advancement, cancellation, supersession, queue redelivery, DLQ, late-result applicability and receipt durability independent of EDA2 TTLs.
- Claim/report: no citation → no causal claim; contradiction blocks approval; exact-byte report review invalidates on relevant dependency change.
- Scale: index freshness/ranking, result paging, per-case/global budget, queue back-pressure and gateway rate limit.

### Evaluation corpus

Use at least the assignment minimum plus realistic variants: code/schema mismatch; missing row; stale cache/replica; worker/backlog/DLQ; duplicate/lost acknowledgement; provider accepted but later undelivered; permission/rate limit; UI visibility issue; misleading deployment; prompt regression; retrieval filter issue; tool/handoff/shared-state failure; two faults; ambiguous/false alarm; missing/contradictory telemetry; untrusted retrieved instruction; investigator tool failure.

Compare with one agent receiving the **same** source access, tools, budgets and evidence limits. Measure boundary localisation, grounded causal accuracy, multiple-cause coverage, safe abstention/inappropriate certainty, citations/coverage, tool cost, latency and operator usefulness. Do not claim the multi-agent design is superior before this evaluation.

### Production operations

Monitor source catalogue freshness, connector health/permission drift, replica lag, code-index lag, query rejection/timeout rate, queue age/DLQ, task retry/supersession, callback-inbox recovery, kill-switch state, role schema failures, D7 block rate, report delivery guard failures, PII redaction findings, cost/budget and source evidence coverage. Alert on broken connectors, not just LLM errors.

## 12. Inputs we still need from the organisation

1. First pilot service, environments/regions and an incident corpus with ground truth.
2. Repository host access model and ownership/service catalog or deployment metadata.
3. Approved telemetry, cloud, CI/CD and AI trace products/accounts/retention.
4. A dedicated read replica plus history/audit source; approved views, classification and tenant model.
5. Identity/secret management, network path to the private gateway and security/data/legal approval.
6. Human report audience, escalation/HITL policy, retention/residency and success metrics.

Until these are supplied, the system can be designed and tested with fixtures but cannot truthfully investigate the organisation’s live incidents.

## 13. Final review checklist

- [ ] No D2 has reappeared; D1/D7 have distinct duties.
- [ ] Every source is a configured opaque catalogue entry, not an LLM-guessed endpoint.
- [ ] The gateway—not the model/Worker—holds source credentials and reaches private sources; the Worker-to-gateway bridge is positively tested and wrong identities are denied.
- [ ] Code evidence is bound to deployed revision, environment and instance where available.
- [ ] D5 uses a network-restricted read-only replica role with revoked function execution; trusted scope mapping and history completeness are not confused with current state.
- [ ] Query, tenant, timing, version, redaction and coverage receipts are persisted.
- [ ] D7 reviews the exact report and dependencies; incomplete is a valid safe result.
- [ ] Queue retry/DLQ/callback/supersession rules cannot silently create duplicate or stale conclusions; case-level inbox/outbox records survive EDA2 TTLs.
- [ ] The same-tool baseline and holdout evaluation exist before any “better diagnosis” claim.

## Source-review pointers

The code facts above come from local, read-only review of the named checkout: apps/kookarcore/app/eda2/AGENTS.md, envelope.py, directory.py, dispatcher.py, app/services/eda/cf_dispatch_service.py, apps/kookar-workers/src/runtime/agent-factory.ts, runtime/invoke.ts, src/queue/consumer.ts, callback.ts and runs.ts, plus Core Supabase/settings/migration/service files. Source review found a useful EDA2/Worker execution pattern, but not an existing safe incident data connector or a complete durable investigator case model. The detailed exact interface contracts remain in the files linked from research/README.md.

### Exact local evidence inspected

| Local checkout path and lines | Source fact used by this plan |
| --- | --- |
| apps/kookarcore/app/eda2/AGENTS.md:6–54 plus engine.py:45–47 | Core routes request → directory/dispatcher → Worker Queue → result callback and owns workflow/HITL decisions; existing engine state has finite Redis TTL, so the new durable case ledger remains required. |
| apps/kookarcore/app/eda2/dispatcher.py:38–106, 112–198 | Requests are deduplicated, scope-superseded, dispatched, then result-handled before workflow advancement. |
| apps/kookarcore/app/services/eda/cf_dispatch_service.py:130–227 | A Core-side dispatch path stores callback context and moves oversized state by reference before enqueueing. |
| apps/kookar-workers/src/runtime/agent-factory.ts:98–183 and runtime/invoke.ts:144–222 | Worker agent construction shares house-log/context/role/model/prompt/output middleware; invokes have timeout/failure handling. |
| apps/kookar-workers/src/queue/consumer.ts:76–198, 217–259; callback.ts:32–81; runs.ts:1–87 | Queue retry/DLQ/callback behavior and best-effort redelivery bookkeeping exist, but are not an authoritative case ledger. |
| apps/kookarcore/app/services/supabase.py:79–121, 150–259 | Existing Core client uses application service credentials and exposes generic select/mutation/RPC helpers; it is unsuitable as an investigator’s read-only connector. |
| apps/kookarcore/supabase/migrations/20260101000000_baseline.sql:52704–52732, 52784 | Some current migration RLS/service-role policies are broad; tenant isolation must be enforced by the proposed connector/policy, then verified in the deployed database. |
| .github/workflows/kookarcore-aca-deploy.yml:64–150 | Current Core CI deploys Azure ACA with GitHub OIDC, Key Vault/managed identity configuration, revision health check and traffic routing. |
| apps/kookar-workers/wrangler.jsonc:17–24, 25–58, 61–83 | Worker custom-domain/Access pattern, queues, retry/DLQ, queue shards and separated variables/secrets are existing operational patterns. |
| infra/loki-pipeline/README.md:1–37 and app/utils/logger.py:29–58, 191–208 | Existing structured logging/Loki guidance can inform correlation/audit, but correlation IDs should not become high-cardinality labels. |

These are source observations from the local copy—not assertions that every mentioned platform, policy or source is currently live in every environment.
