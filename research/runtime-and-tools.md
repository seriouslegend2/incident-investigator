# How the agents actually run

Status: proposed implementation, not a deployed system. Seven agents: D1, D3, D4, D5, D6, D7 and D8. D2 remains removed. This page explains the machinery; [each agent](agents/README.md) defines its job and [the tool catalog](tool-catalog.md) defines exact tool arguments/results.

## 1. Where everything lives

| Component | Location in the proposed first implementation | What it contains |
| --- | --- | --- |
| Investigation backend | One deployed service/container, on a VM or another suitable host | Agent runner, tool functions, authorization checks, case state and artifact handling. Separate machine per agent is not required. |
| D1/D3–D8 | Separate logical runs inside that backend | Instructions, task-specific conversation/context, allowed tools and a structured-output schema. Not seven trained models or seven chat installations. |
| LLM | Configured model-provider API | Receives bounded context and tool descriptions; returns tool requests or a structured answer. It does not connect to production sources by itself. |
| Application code | GitHub/GitLab or other configured repositories; optional read-only local checkouts and code-search indexes | Source remains outside the LLM context. A connector searches/fetches selected files at an exact revision. |
| Database | Existing database infrastructure; D5's record reads target an approved read replica | No database copy inside the model or investigator VM is required. |
| Deployment information | Existing CI/CD, artifact registry, cloud/container control plane and deployment records | Read-only adapters retrieve release, artifact, source and configuration bindings. |
| Logs/metrics/traces | Existing configured AWS/Azure/GCP or other telemetry platform | Queries run against the actual store, not a presumed universal cloud log endpoint. |
| Application-agent evidence | Existing AI tracing/prompt/workflow stores | Actual retained rendered prompts, retrieval/tool results and handoff records, where available. |
| Case/evidence store | Investigator-owned storage | Source references, authorized evidence excerpts, task/results, immutable report drafts and audit events. Writes here do not authorize application/database changes. |
| Credentials | Backend connector secret storage/workload identity | Never included in agent input, search results or rendered prompts. |

The backend needs network connectivity to those sources, for example through the organization's private network. A laptop can run the prototype; hosting does not create reasoning capability. For the assignment, simulated adapters can implement the same contracts, clearly labeled simulated rather than live integrations.

## 2. A real agent is a loop—not one input/output call

```text
D1 assigns a bounded task to D4
          ↓
Backend prepares instructions + task + relevant shared findings + permitted tool schemas
          ↓
Call LLM
          ↓
LLM returns tool name + arguments ──→ Backend validates permission and limits
          ↑                                      ↓
          └──── bounded tool result ←── Connector queries the actual source
          |
          └── Repeat until structured final answer, cancellation or budget limit
                                  ↓
                   Backend validates, wraps and stores the result
                                  ↓
                   D1 receives findings + gaps + evidence references
```

The model chooses what to inspect. Ordinary software executes the request. Agents can have many model turns per task. A tool can be a normal Python/TypeScript function calling a platform SDK/API; MCP is an optional transport, not a requirement. No separate OpenClaw, Claude Code or Codex installation is required per specialist. An existing suitable runner could be used instead of writing the loop, but permissions, provenance and output contracts still need implementation.

The proposed implementation exposes bounded functions rather than an unrestricted terminal. Search, file navigation and schema inspection are still iterative. Use source content as untrusted evidence, not instructions. Do not execute repository scripts or application agents just because a retrieved file requests it.

## 3. Setup before the first incident

These are ordinary configuration/infrastructure tasks, not additional reasoning agents:

1. Register approved sources with opaque IDs: repositories, database replicas, telemetry backends, deployment/config stores and AI traces. Record environment, owner, capability, retention, index freshness and missing metadata.
2. Bind connector-side credentials and least-privilege policies. Enforce tenant/resource access before returning metadata or content. A model-supplied filter cannot widen the trusted policy.
3. For small repositories, maintain read-only checkouts; for large estates, use existing version-aware indexed code search and bounded exact-revision fetches. Sync/index workers, not the LLM, keep searchable content current. Index lag and missing languages/revisions remain visible.
4. Register supported adapter operations and schemas. An unavailable integration returns `unsupported`/a catalog gap; it is not secretly available because it appears in a diagram.
5. Configure budgets and the D7 review/delivery policy. Source reads and investigator-owned writes have different capabilities.

Example: `repo:delivery`, `db:messaging-replica`, `logs:delivery-prod` and `deploy:delivery-prod` are invented catalog IDs, not hidden incident evidence. A catalog association is a discovery lead, not proof of actual runtime use.

## 4. Precisely what reaches the model

| Part | Supplied by | Contents |
| --- | --- | --- |
| Role instructions | Backend configuration | Responsibility, grounding/security rules, allowed stopping behavior, current runtime clock and nonsecret bounded discovery defaults. |
| Task-v1 | Runtime, using a validated D1 assignment | Question, known premises, unknowns, scope, dependencies, relevant knowledge refs/excerpts, role-specific input and limits. |
| Tool schemas | Runtime capability registry | Only the tool names/arguments allowed for that run; the full permitted registry can be discovered incrementally. |
| Tool results | Connectors through the runtime | Small result pages/excerpts, original evidence refs, actual scope, freshness, completeness and errors. |
| Model final answer | LLM | `AgentAnswer-v1`: observations, interpretations, gaps, coverage references, follow-up proposals and a role-specific structured object. |
| Result-v1 | Runtime, not the LLM | Model answer plus trusted task/attempt/revision identity, original tool receipts and measured costs. |

Runtime keeps caller identity, credential handles, policy and remaining global limits outside model-controlled authority. Task scope describes requested work; it is not a permission grant. The model must not manufacture evidence IDs, deployment bindings, approval tokens, hashes or usage totals.

At a model call, send only this role/task's permitted tool definitions and output schema—not the complete JSON registry or all seven conversations. The schema files describe application validation; a provider adapter must map them to its supported structured-output/tool schema subset, then validate the returned answer locally. Tool availability can be loaded incrementally. This schema adaptation is not implemented here.

When parallel work finishes, the task runtime resumes D1 with new result references and a compact updated case snapshot. D1 can fetch relevant originals. It does not continuously receive every specialist token, and it need not busy-poll all sources. Context compaction keeps source/version references and explicit gaps; it is not permission to discard counterevidence.

If the incident time is unknown, a telemetry discovery query can use the configured bounded recent lookback anchored to the runtime clock/source observation timestamp. Record that interval as a search assumption, not the actual incident time. Return the actual searched interval; broaden within policy/budget or clarify rather than silently assume the complaint is recent. A connector resolves an authorized source ID to its configured endpoint, cloud project/account/region and credential binding; the LLM does not guess URLs, database hosts or cloud accounts.

See the [shared protocol](agent-protocol.md) for lifecycle semantics, and the [machine-readable schemas and examples](contracts/README.md) for exact required/nullable fields. JSON examples are synthetic teaching fixtures—not actual source evidence or diagnosed incidents. Token/scan limits in examples illustrate a contract; they are not measured production defaults.

## 5. Code-to-data handoff: how D5 knows what to query

Responsibility is specialized; knowledge is shared. D5 must understand the relevant application read contract. It is not handed credentials plus “check the database.” D4 can inspect schema evidence; D5 can fetch the cited code excerpt. D1 coordinates deeper cross-domain work; no uncontrolled peer spawning is required.

| Event | Input/question | Output that enables the next step |
| --- | --- | --- |
| D1 → D4 discovery | “Locate how customer-group destinations are resolved.” No table or filename assumed. | Repository/commit/file references; implementation inputs and reads; candidate connection, relation, keys, predicates, selected field, transform, failure branches and unknown bindings. |
| D7 premise check | Discovered read contract plus original code and binding evidence | Accept the scoped implementation fact, or require correction; runtime attribution can remain unresolved. |
| D1 → D5 | Shared read-contract reference and relevant code excerpt; affected entity and incident time if discovered | D5 resolves the permitted replica, inspects actual schema, checks lookup semantics and queries minimum necessary values/history. |
| D5 → D1 → D4, when needed | Actual schema/data contradict the implementation or a binding is missing | A targeted follow-up, not a guessed replacement table or an assumed migration. |

The [ReadContract schema](contracts/agent-io.schema.json) records those discovered details and uncertainty. A read-contract artifact is stored by the runtime from accepted findings; its ID is not invented by D4. A code connection name must be resolved to its environment-specific database identity. The authorized replica is then mapped to that identity; it is not inferred from a similar name.

For exact tool-by-tool request and response JSON, open the [code-to-replica tool flow](contracts/tool-flow-example.json). It includes the actual arguments, typed row/column result, coverage/freshness receipt and a timeout alternative. All data there is synthetic.

D5 can begin with schema discovery when code is not yet located: `catalog.search` for candidate data sources, `data.inspect_schema` for bounded metadata, then return candidate relations and the missing application link. Schema names alone do not establish which table the service uses. D1 can ask D4 to verify that link. Investigation may proceed code → data or data → code.

## 6. Replica policy and temporal correctness

Record queries use approved replicas with a dedicated least-privilege identity. Do not reuse the application's privileged service key. Connector-side relation/column/tenant rules, safe query compilation, timeout/scan/result caps and read-only transactions are required. No arbitrary SQL/RPC/function execution; allowlisted templates must themselves be reviewed for side effects. Metadata/diagnostics that a replica cannot provide remain gaps or use a separately authorized read-only monitoring API—never an automatic primary fallback.

`data.read_bounded` reads current state. `data.history` uses an actual configured audit/change-history source; a timestamp argument cannot make an ordinary replica a historical database. Return observation time, available replay watermark/lag and unknown freshness. A missing replica row is not alone proof that the application saw missing data. An inaccessible table, empty result, partial query, missing history and schema mismatch are distinct outcomes.

## 7. One concrete propagation example

Invented names below are discovered outputs inside the example, not values given by the user:

```text
User: “The customer group did not receive the message.”
D1 → catalog: find candidate messaging sources; ambiguity stays visible.
D1 → D3: locate matching attempts → E1 identifies attempt M17 and a resolution failure.
D1 → D4: explain that stage → E3 establishes deployed lookup; RC1 records its data read.
D1 → D7: check new RC1 premises; correct gaps before concrete cross-domain use.
D1 → D5: RC1 + cited code + discovered customer/time → inspect schema, read replica/history.
D5 → D1: current fields + E2; incident-time values unknown → request history, not a causal claim.
D1 → selected follow-up agents: close the specific gaps, or preserve them if unavailable.
D1 → D8: draft from scoped supported claims and limitations.
D1 → D7: review exact stored report bytes and dependencies.
Runtime: deliver only while approval remains valid; otherwise revise or return incomplete.
```

No automatic all-agent fan-out, no mandatory D3-first policy, no D2. This example is one possible path; an AI-quality issue can begin with D6, and a feature-discovery task can begin with D4.

## 8. Failures, budgets and what is not claimed

The runtime caps both backend work and response size, counts all model/tool/review attempts, and cancels bounded work when limits expire. Read-only queries can still be expensive. Source errors remain distinct from investigator/model errors. D1 can propose a different query/source or clarification, not infinite retries.

Malformed outputs get a bounded schema-repair attempt; after exhaustion, runtime emits a failed/partial task record and preserves actual evidence receipts. D7 failure never implies acceptance. Source evidence stays versioned; approved reports are immutable and checked again at delivery. See the [shared lifecycle rules](agent-protocol.md).

These documents define a design and interfaces. They do not install cloud connectors, sync repositories, create replicas, run an agent or prove multi-agent superiority. The single-agent evaluation baseline must receive the same sources/tools/permissions; measure whether specialization and review justify their overhead.
