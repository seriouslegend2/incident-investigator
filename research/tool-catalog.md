# Exact tool catalog

Status: proposed interfaces, not installed adapters. Generated from [definitions.mjs](contracts/definitions.mjs); 41 operations. Seven agent IDs; no D2. Start with [where tools execute](runtime-and-tools.md). All nested types and bounds are defined in [tool-contracts.json](contracts/tool-contracts.json).

## Common calling convention

The model requests a tool name and its JSON arguments. Every input below requires every listed key, including `limits`; use `null` only where nullable, and `[]` for an empty list. Server caps override model limits. An empty filter cannot bypass tenant policy. Source references must come from authorized discovery; no credentials are arguments. All tool returns use the shared receipt below; operation-specific fields belong inside `data`.

`ToolLimits` = {max_items: positive integer, timeout_ms: positive integer, max_output_bytes: positive integer, max_scan_bytes: nonnegative integer or null}. Null means use the connector's enforced default cap, not unlimited work.

`ToolReceipt` = {call_ref, tool, status, data, evidence_refs, coverage, next_cursor, error, cost}. Exact schema: [tool-receipt.schema.json](contracts/tool-receipt.schema.json). The runtime records the receipt; the LLM does not manufacture it.

| Status | Meaning |
| --- | --- |
| `ok` | Requested operation completed with returned data. Does not imply a diagnosis. |
| `empty` | A successful search/read has no matches within recorded scope; `data` contains typed empty collections. Not global absence. |
| `partial` | Useful data exists but pages/partitions/ranges/retention or another prerequisite are incomplete. |
| `denied` | Trusted policy disallowed the operation; no permission-sensitive data leaks. |
| `not_found` | A specific authorized resource/revision could not be resolved. Not an empty general search. |
| `unsupported` | The configured connector lacks this operation/history/revision. |
| `timeout` / `error` | Execution failed; error carries code/message/retryability. No automatic negative finding. |

For a hard failure with no usable result, `data=null`; partial results must still match that tool's data schema. Control operations may return operational status `ok` while their own data says pending/queued. Source evidence refs may be empty for a control operation.

Coverage records actual scope, query description, source snapshots, source observation/watermark/lag/index freshness, sampling/retention, completeness, pagination and scanned bytes. Unknown values are null, not fabricated. A receipt is provenance of a query, not causal proof. See [lifecycle protocol](agent-protocol.md).

## Role access profiles

The agent lists below are maximum eligible capabilities, not a permission grant. Runtime intersects role, task, authenticated tenant/source permissions and remaining budget. D7 source tools are bounded verification only. D8 cannot explore production sources; it fetches assigned originals and writes investigator-owned drafts.

## catalog.search

Find candidate sources/services/repos by feature terms; does not establish the failing component.

Agents: **D1, D3, D4, D5, D6, D7**. Executes against: Configured source/service directory.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `query` | string |
| `kinds` | array<"service" / "repository" / "database" / "replica" / "telemetry" / "deployment" / "configuration" / "ai_workflow" / "history" / "cache" / "index"> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `candidates` | array<Source> |

Guard/limitation: Authorization filters metadata before return; bounded indexed discovery, not raw estate scanning.

## catalog.describe

Describe one discovered source, capabilities, relationships and freshness.

Agents: **D1, D3, D4, D5, D6, D7**. Executes against: Configured source/service directory.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `entity_ref` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `source` | Source |
| `relationships` | array<{from_ref: string, to_ref: string, kind: string, basis: "declared" / "indexed" / "runtime_observed", evidence_refs: array<string>}> |

Guard/limitation: Declared relationships are leads, not automatically runtime truth.

## history.search

Retrieve useful precedent or intended-behavior documents.

Agents: **D1, D7**. Executes against: Authorized runbook/contract/past-incident index.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `query` | string |
| `entity_refs` | array<string> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `items` | array<SourceItem> |

Guard/limitation: No ground-truth labels or future fixes from held-out evaluation cases; precedent is not current causal proof.

## case.read

Read a bounded current, review or report snapshot and its references.

Agents: **D1, D3, D4, D5, D6, D7, D8**. Executes against: Investigator-owned case store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `view` | "current" / "review" / "report" |
| `snapshot_ref` | string or null |
| `sections` | array<"scope" / "claims" / "hypotheses" / "results" / "unknowns" / "coverage" / "reviews" / "reports" / "read_contracts"> |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `snapshot_ref` | string |
| `case_revision` | integer |
| `scope_revision` | integer |
| `artifact_refs` | array<string> |
| `excerpts` | array<Excerpt> |

Guard/limitation: D8 restricted to assigned report snapshot; D7 gets independent review snapshot.

## evidence.fetch

Fetch cited original excerpts or accepted shared artifacts, including code-to-data read contracts.

Agents: **D1, D3, D4, D5, D6, D7, D8**. Executes against: Evidence registry plus authorized original-source fetch.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `refs` | array<string> |
| `selectors` | array<string> |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `excerpts` | array<Excerpt> |
| `read_contracts` | array<ReadContract> |
| `artifact_refs` | array<string> |

Guard/limitation: Recheck access on every fetch; selectors/ranges are bounded, secrets redacted, no unrestricted URL fetch.

## delegate_task

Validate a task proposal, reserve budget and enqueue it once; runtime assigns IDs/revisions.

Agents: **D1**. Executes against: Investigator task runtime.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `idempotency_key` | string |
| `proposal` | TaskProposal |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `task_ref` | string |
| `state` | "queued" / "waiting_prerequisites" / "existing" |
| `effective_budget` | Budget |

Guard/limitation: Validate role_input against target Task schema; clamp limits, check prerequisites and review gates; same key returns same task.

## request_clarification

Record and present a focused missing-scope question to the user.

Agents: **D1**. Executes against: Investigator UI/request channel.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `question` | string |
| `candidate_refs` | array<string> |
| `why_needed` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `clarification_ref` | string |
| `state` | "pending" / "answered" |
| `answer` | string or null |

Guard/limitation: Pending means no user answer yet; agent cannot manufacture one or keep investigating an arbitrarily chosen candidate.

## telemetry.describe_sources

Inspect queryable fields, retention, sampling and supported correlation/status operations.

Agents: **D3, D7**. Executes against: Configured telemetry source metadata APIs.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_refs` | array<string> |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `sources` | array<{source_ref: string, fields: array<string>, operations: array<string>, retention: string or null, sampling: string or null, limitations: array<string>}> |

Guard/limitation: No implied cloud integration when the source/operation is unconfigured.

## telemetry.aggregate

Run bounded counts/rates/distributions to narrow time, service or cohort.

Agents: **D3, D7**. Executes against: Actual log/metric/event backend.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `time_range` | TimeRange |
| `filters` | array<{field: string, op: "eq" / "neq" / "in" / "lt" / "lte" / "gt" / "gte" / "is_null" / "not_null", value: string / number / boolean / null or array<string / number / boolean / null>}> |
| `group_by` | array<string> |
| `measure` | "count" / "error_rate" / "latency" |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `groups` | array<{keys: array<EntityKey>, value: number, unit: "count" / "ratio" / "milliseconds", denominator: number or null, semantics: "exact" / "approximate" / "lower_bound"}> |

Guard/limitation: Validate fields and denominator/units; scan caps plus page caps; no arbitrary backend query language.

## telemetry.query_events

Fetch relevant original log/event records using validated terms, IDs and filters.

Agents: **D3, D7**. Executes against: Actual configured logs/events store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `time_range` | TimeRange |
| `search_terms` | array<string> |
| `filters` | array<{field: string, op: "eq" / "neq" / "in" / "lt" / "lte" / "gt" / "gte" / "is_null" / "not_null", value: string / number / boolean / null or array<string / number / boolean / null>}> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `events` | array<SourceItem> |

Guard/limitation: Distinguish event/ingestion time; query exhaustion is not proof of absent execution.

## telemetry.fetch_trace

Read a specific trace and bounded span summaries/links.

Agents: **D3, D7**. Executes against: Tracing backend.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `trace_id` | string |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `trace_id` | string |
| `spans` | array<{span_ref: string, parent_ref: string or null, links: array<string>, service_ref: string or null, operation: string, status: string, evidence_refs: array<string>}> |

Guard/limitation: Trace sampling/partial retention exposed; async work need not share a single trace.

## telemetry.correlate_messages

Find records joined through discovered request/job/message/run keys.

Agents: **D3, D7**. Executes against: Configured message/job correlation indexes.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_refs` | array<string> |
| `keys` | array<CorrelationKey> |
| `time_range` | TimeRange |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `links` | array<{from_ref: string, to_ref: string, key: CorrelationKey, certainty: "exact_key" / "candidate", evidence_refs: array<string>}> |

Guard/limitation: Time proximity alone cannot become an exact join.

## telemetry.read_status

Read a discovered queue backlog, worker state or message delivery receipt.

Agents: **D3, D7**. Executes against: Queue/worker/provider read-only APIs.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `kind` | "queue" / "worker" / "provider_message" |
| `entity_ref` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `items` | array<{entity_ref: string, status: string, meaning: string, observed_at: string, evidence_refs: array<string>}> |

Guard/limitation: Provider acceptance, delivery and user visibility are separate meanings; no sends/retries/queue mutations.

## code.search

Locate candidate paths, text matches or symbols across authorized repositories.

Agents: **D4, D7**. Executes against: Read-only checkouts or version-aware code index.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `repository_refs` | array<string> |
| `revision` | string or null |
| `kind` | "paths" / "text" / "symbols" |
| `query` | string |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `matches` | array<{location: SourceLocation, excerpt: string, match_kind: "path" / "text" / "symbol", navigation_basis: "text" / "indexed_symbol", limitations: array<string>}> |

Guard/limitation: Empty repo list means bounded authorized catalog/index discovery only; never an unlimited raw clone/scan. Revision null permits discovery, not deployed attribution.

## code.read_at_revision

Read an exact versioned file range; no execution of its code.

Agents: **D4, D7**. Executes against: Repository API or immutable checkout.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `repository_ref` | string |
| `commit` | string |
| `path` | string |
| `start_line` | integer |
| `end_line` | integer |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `location` | SourceLocation |
| `content` | string |

Guard/limitation: Require resolved immutable commit, validated path containment, line/byte caps and secret redaction. No silent latest-branch fallback.

## code.references

Find definitions, callers or references to a discovered symbol.

Agents: **D4, D7**. Executes against: Language/symbol indexes with text fallback.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `location` | SourceLocation |
| `symbol` | string |
| `direction` | "definition" / "callers" / "references" |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `matches` | array<{location: SourceLocation, basis: "precise_index" / "text_candidate", excerpt: string}> |

Guard/limitation: Mark unresolved dynamic dispatch/cross-repo index gaps; static references do not prove actual calls.

## code.diff

Compare two discovered immutable source revisions.

Agents: **D4, D7**. Executes against: Repository version-control API/index.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `repository_ref` | string |
| `base_commit` | string |
| `head_commit` | string |
| `paths` | array<string> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `changes` | array<{path: string, patch_excerpt: string, evidence_refs: array<string>}> |

Guard/limitation: A recent change is a candidate, not automatically the cause.

## build.provenance

Resolve a built artifact to recorded source inputs and build identity.

Agents: **D4, D7**. Executes against: CI/artifact provenance store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `artifact_ref` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `artifact_ref` | string |
| `source_locations` | array<SourceLocation> |
| `build_ref` | string or null |
| `verification` | "verified_record" / "unverified_record" / "unavailable" |
| `evidence_refs` | array<string> |

Guard/limitation: One artifact may have multiple repository inputs; provenance presence is not deployed activation.

## deploy.history

Read releases, failed rollouts and placement changes in a bounded interval.

Agents: **D4, D7**. Executes against: Configured CI/CD/cloud/container deployment API.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `service_ref` | string |
| `environment` | string |
| `time_range` | TimeRange |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `deployments` | array<{deployment_ref: string, service_ref: string, artifact_ref: string or null, status: string, changed_at: string, evidence_refs: array<string>}> |

Guard/limitation: Read-only metadata; failed deployment may never have served traffic.

## deploy.instance_binding

Bind the affected instance/attempt time to artifact/config where recorded.

Agents: **D4, D7**. Executes against: Runtime instance inventory and release records.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `service_ref` | string |
| `environment` | string |
| `instance_ref` | string or null |
| `event_time` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `bindings` | array<{instance_ref: string or null, artifact_ref: string or null, config_refs: array<string>, interval: TimeRange or null, evidence_refs: array<string>, unknowns: array<string>}> |

Guard/limitation: Preserve mixed rollout cohorts and missing historical records; do not infer a shared SHA.

## config.effective

Inspect effective nonsecret settings, connection identities and secret-version metadata.

Agents: **D4, D7**. Executes against: Read-only effective configuration/feature-flag metadata.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `service_ref` | string |
| `environment` | string |
| `instance_ref` | string or null |
| `keys` | array<string> |
| `event_time` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `settings` | array<{key: string, value: string / number / boolean / null, redacted: boolean, version_ref: string or null, effective_at: string or null, related_source_ref: string or null, evidence_refs: array<string>}> |

Guard/limitation: Historical lookup only if backend supports it; connection identity may be returned, credential values must not.

## config.history

Read recorded setting changes and effective intervals.

Agents: **D4, D7**. Executes against: Retained configuration/flag audit store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `service_ref` | string |
| `environment` | string |
| `keys` | array<string> |
| `time_range` | TimeRange |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `changes` | array<SourceItem> |

Guard/limitation: No current-value substitution for missing historical config.

## infra.inspect

Inspect a discovered infrastructure resource or policy for a bounded question.

Agents: **D4, D7**. Executes against: Authorized read-only cloud/container/network/IAM APIs.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `resource_ref` | string |
| `kind` | "runtime" / "network" / "permission" / "storage" |
| `question` | string |
| `event_time` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `findings` | array<{condition: string, observed_at: string, evidence_refs: array<string>, limitations: array<string>}> |

Guard/limitation: No active network experiments, command execution, restarts or permission changes. Historical state may be unavailable.

## data.describe_source

Resolve database identity, replica relationship, query/history support and freshness.

Agents: **D4, D5, D7**. Executes against: Configured database/data-source directory and read-only metadata.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `source` | Source |
| `primary_identity_ref` | string or null |
| `replica` | boolean |
| `schema_search_supported` | boolean |
| `history_source_refs` | array<string> |
| `replay_watermark` | string or null |
| `lag_ms` | integer or null |

Guard/limitation: No privileged connection string is returned. An unavailable replica is not permission to query primary.

## data.inspect_schema

Search permitted relation/column metadata or describe a discovered relation.

Agents: **D4, D5, D7**. Executes against: Approved replica/catalog metadata.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `query` | string |
| `relation` | string or null |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `schema_ref` | string |
| `relations` | array<{relation: string, kind: "table" / "view" / "materialized_view", columns: array<{name: string, type: string, nullable: boolean}>, keys: array<array<string>>, relationships: array<string>, evidence_refs: array<string>}> |

Guard/limitation: Bounded metadata search; relation names alone do not establish application usage.

## data.read_bounded

Execute a validated parameterized read or an approved read template.

Agents: **D5, D7**. Executes against: Approved read-replica connector.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `schema_ref` | string |
| `read_contract_ref` | string or null |
| `relation` | string |
| `columns` | array<string> |
| `filters` | array<{field: string, op: "eq" / "neq" / "in" / "lt" / "lte" / "gt" / "gte" / "is_null" / "not_null", value: string / number / boolean / null or array<string / number / boolean / null>}> |
| `order_by` | array<{field: string, direction: "asc" / "desc"}> |
| `query_template_ref` | string or null |
| `template_parameters` | array<EntityKey> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `columns` | array<{name: string, type: string, redacted: boolean}> |
| `rows` | array<array<JsonValue>> |
| `query_ref` | string |
| `query_observed_at` | string |
| `replay_watermark` | string or null |
| `lag_ms` | integer or null |

Guard/limitation: Current-state read only. Backend validates identifiers/operators, tenant restrictions, template semantics and cost. No arbitrary SQL/functions or primary fallback; rows follow column order.

## data.history

Read retained changes/historical values for an established data scope.

Agents: **D5, D7**. Executes against: Actual configured audit/CDC/versioned history source.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `history_source_ref` | string |
| `read_contract_ref` | string or null |
| `relation` | string |
| `entity_keys` | array<EntityKey> |
| `fields` | array<string> |
| `time_range` | TimeRange |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `changes` | array<{valid_from: string or null, valid_to: string or null, fields: array<EntityKey>, transaction_ref: string or null, evidence_refs: array<string>}> |
| `historical_state_established` | boolean |
| `limitations` | array<string> |

Guard/limitation: Audit completeness/ordering must support the claimed interval; a plain replica cannot time-travel. Unsupported history remains unknown.

## data.lineage

Find established views, transformations, replica/cache/index relationships.

Agents: **D5, D7**. Executes against: Registered data lineage and retained transform records.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `relation` | string |
| `direction` | "upstream" / "downstream" |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `links` | array<{from_ref: string, to_ref: string, transformation: string, basis: "declared" / "implementation" / "runtime_observed", evidence_refs: array<string>}> |

Guard/limitation: Declared lineage is not proof the failing run followed it.

## data.diagnostics

Read available query-plan metadata/statistics, locks, connection or replication health.

Agents: **D5, D7**. Executes against: Approved read-only database monitoring interface.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `kind` | "plan" / "statistics" / "locks" / "connections" / "replication" |
| `query_ref` | string or null |
| `time_range` | TimeRange or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `findings` | array<{metric: string, value: string / number / boolean / null, unit: string or null, observed_at: string, evidence_refs: array<string>, limitations: array<string>}> |

Guard/limitation: Plan inspection cannot use executing ANALYZE or unsafe functions. Primary-only facts need separately approved monitoring, not a privileged DB session.

## data.read_cache_index

Read narrowly identified cache entries or indexed documents and version/TTL metadata.

Agents: **D5, D7**. Executes against: Discovered cache/search-index read connector.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `source_ref` | string |
| `read_contract_ref` | string or null |
| `key_refs` | array<string> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `items` | array<{key_ref: string, fields: array<EntityKey>, version_ref: string or null, expires_at: string or null, evidence_refs: array<string>}> |

Guard/limitation: Source must first exist in authorized metadata/evidence; no cache presumed, no invalidation/reindex/write.

## ai.list_workflows

Discover candidate application workflows by feature terms.

Agents: **D6, D7**. Executes against: Configured AI workflow/run directory.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `query` | string |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `workflows` | array<Candidate> |

Guard/limitation: Application-agent workflows, not investigator hidden reasoning.

## ai.list_runs

Find runs matching discovered scope, including successful-status quality failures.

Agents: **D6, D7**. Executes against: Actual configured AI tracing store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `workflow_refs` | array<string> |
| `time_range` | TimeRange or null |
| `search_terms` | array<string> |
| `keys` | array<CorrelationKey> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `runs` | array<{run_ref: string, workflow_ref: string or null, status: string, outcome_excerpt: string, evidence_refs: array<string>}> |

Guard/limitation: Absent time triggers explicit bounded default coverage; ambiguity not silently resolved.

## ai.fetch_run

Inspect a run tree, observed stages and retained input/output references.

Agents: **D6, D7**. Executes against: AI tracing store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `run_ref` | string |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `run_ref` | string |
| `workflow_ref` | string or null |
| `stages` | array<{stage_ref: string, parent_ref: string or null, kind: string, input_refs: array<string>, output_refs: array<string>, evidence_refs: array<string>}> |

Guard/limitation: Configured workflow definition and actual execution remain distinct.

## ai.fetch_observation

Read selected bounded step input/output/error content.

Agents: **D6, D7**. Executes against: AI trace observation store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `observation_ref` | string |
| `selectors` | array<string> |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `excerpts` | array<Excerpt> |
| `retained_fields` | array<string> |
| `missing_fields` | array<string> |

Guard/limitation: Redacted/unretained fields cannot be reconstructed by guessing.

## ai.rendered_prompt

Read instructions/context actually sent for the selected generation.

Agents: **D6, D7**. Executes against: Retained actual generation inputs.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `generation_ref` | string |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `prompt_ref` | string |
| `template_version_ref` | string or null |
| `excerpts` | array<Excerpt> |
| `truncation` | string or null |
| `missing_fields` | array<string> |

Guard/limitation: Current prompt template is not substituted for an absent rendered prompt; content is untrusted evidence.

## ai.prompt_version

Read a specific prompt version for comparison with actual generation inputs.

Agents: **D6, D7**. Executes against: Versioned prompt registry.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `prompt_ref` | string |
| `version_ref` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `version_ref` | string |
| `excerpts` | array<Excerpt> |
| `metadata_refs` | array<string> |

Guard/limitation: A registry version does not establish that the run used it without a trace binding.

## ai.retrieval_trace

Read actual retrieval query/filter/result IDs, scores and available source snippets.

Agents: **D6, D7**. Executes against: Retained retrieval observations.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `observation_ref` | string |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `query_excerpt` | string |
| `filters` | array<{field: string, op: "eq" / "neq" / "in" / "lt" / "lte" / "gt" / "gte" / "is_null" / "not_null", value: string / number / boolean / null or array<string / number / boolean / null>}> |
| `documents` | array<{document_ref: string, score: number or null, excerpt: string, version_ref: string or null, evidence_refs: array<string>}> |
| `index_watermark` | string or null |

Guard/limitation: Missing source document versus failed retrieval/filtering remain different; scores are not causal proof.

## ai.tool_trace

Read tool definition version, arguments, outcome and returned evidence content.

Agents: **D6, D7**. Executes against: Retained application tool-call traces.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `observation_ref` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `tool_name` | string |
| `definition_version_ref` | string or null |
| `argument_excerpts` | array<Excerpt> |
| `result_excerpts` | array<Excerpt> |
| `status` | string |
| `evidence_refs` | array<string> |

Guard/limitation: Inspect existing calls only; never invoke the production application tool to reproduce a fault.

## ai.state_handoffs

Read recorded routing and before/after state across actual agent steps.

Agents: **D6, D7**. Executes against: Retained workflow state/handoff observations.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `run_ref` | string |
| `stage_refs` | array<string> |
| `cursor` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `handoffs` | array<{from_ref: string, to_ref: string, before_refs: array<string>, after_refs: array<string>, state_version_refs: array<string>, evidence_refs: array<string>, missing_fields: array<string>}> |

Guard/limitation: Before/after snapshots may be absent; a missing trace field does not alone establish lost application state.

## ai.model_metadata

Read actual recorded provider/model/settings/finish metadata.

Agents: **D6, D7**. Executes against: Generation/provider metadata retained in traces.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `generation_ref` | string |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `provider` | string or null |
| `model` | string or null |
| `version_ref` | string or null |
| `settings` | array<EntityKey> |
| `finish_reason` | string or null |
| `evidence_refs` | array<string> |
| `unavailable` | array<string> |

Guard/limitation: Hidden provider versions/internal reasoning remain unavailable, not fabricated.

## report.store_draft

Validate and store structured report content; runtime canonicalizes bytes, computes hash and binds dependencies.

Agents: **D8**. Executes against: Investigator-owned immutable artifact store.

Input arguments (all keys required):

| Field | Type / allowed values |
| --- | --- |
| `idempotency_key` | string |
| `report_snapshot_ref` | string |
| `content` | ReportContent |
| `supersedes_report_ref` | string or null |
| `limits` | ToolLimits |

Successful/partial `data` object:

| Field | Type / allowed values |
| --- | --- |
| `report_ref` | string |
| `report_version` | integer |
| `artifact_hash` | string |
| `dependency_manifest_ref` | string |
| `approval_state` | "unreviewed" |

Guard/limitation: No writer self-approval. Stored content must match submitted structured content; source/claim refs validated, exact artifact goes to D7.

## Shared types and aliases

Exact nested fields are in the JSON schemas. In particular: SourceLocation = repo + immutable commit + path + line range + evidence refs; EntityKey = field + scalar value + evidence refs; Scope = discovered entity/repository refs, tentative feature terms, nullable environment/time range; ReadContract = code caller + discovered connection/relation/lookup fields + version bindings + evidence + gaps.

Previous conceptual names `code.symbol`, `case.read_review_snapshot`, `case.read_report_snapshot` and `ai.list_workflows/runs` are not extra endpoints. Use `code.search(kind="symbols")`/`code.references`, `case.read(view="review")`, `case.read(view="report")` and `ai.list_workflows`/`ai.list_runs`. Generic queue/provider/cache/network/DB diagnostics in older notes map to the concrete tools above. No arbitrary shell, SQL or production mutation tool is exposed.
