// Authoritative proposed interfaces. These schemas do not implement source adapters.
export const S = { type: 'string' };
export const ID = { type: 'string', minLength: 1 };
export const B = { type: 'boolean' };
export const N = { type: 'number', minimum: 0 };
export const I = { type: 'integer', minimum: 0 };
export const E = (...values) => ({ enum: values });
export const A = items => ({ type: 'array', items });
export const O = properties => ({ type: 'object', properties, required: Object.keys(properties), additionalProperties: false });
export const R = name => ({ $ref: `#/$defs/${name}` });
export const Q = schema => ({ anyOf: [schema, { type: 'null' }] });
export const D = (schema, description) => ({ ...schema, description });
export const ids = A(ID);
export const AGENTS = ['D1', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8'];
const investigators = ['D3', 'D4', 'D5', 'D6'];
const sourceReaders = ['D1', ...investigators, 'D7'];
const domainReaders = [...investigators, 'D7'];
const scalar = { type: ['string', 'number', 'boolean', 'null'] };
const scalarList = A(scalar);
const filter = O({ field: ID, op: E('eq', 'neq', 'in', 'lt', 'lte', 'gt', 'gte', 'is_null', 'not_null'), value: { anyOf: [scalar, scalarList] } });

export const defs = {
  JsonValue: { anyOf: [scalar, { type: 'array', items: R('JsonValue') }, { type: 'object', additionalProperties: R('JsonValue') }] },
  Ref: ID,
  TimeRange: O({ start: S, end: S, basis: E('event', 'ingestion', 'query', 'deployment') }),
  Scope: O({ entity_refs: ids, feature_terms: A(S), environment: Q(ID), time_range: Q(R('TimeRange')), repository_refs: ids }),
  Budget: O({ tool_calls_max: I, wall_ms_max: I, model_tokens_max: I, output_tokens_max: I }),
  ToolLimits: O({ max_items: { type: 'integer', minimum: 1 }, timeout_ms: { type: 'integer', minimum: 1 }, max_output_bytes: { type: 'integer', minimum: 1 }, max_scan_bytes: Q(I) }),
  Dependency: O({ ref: ID, version: ID }),
  Premise: O({ claim_ref: ID, evidence_refs: ids }),
  Excerpt: O({ evidence_ref: ID, text: S, locator: S }),
  Knowledge: O({ brief: S, artifact_refs: ids, excerpts: A(R('Excerpt')), read_contract_refs: ids }),
  EntityKey: O({ field: ID, value: scalar, evidence_refs: ids }),
  CorrelationKey: O({ kind: ID, value: ID, evidence_refs: ids }),
  Followup: O({ agent_id: E(...AGENTS), question: S, premise_refs: ids, unknowns: A(S), expected_information: S }),
  SourceLocation: O({ repository_ref: ID, commit: ID, path: ID, start_line: { type: 'integer', minimum: 1 }, end_line: { type: 'integer', minimum: 1 }, evidence_refs: ids }),
  ReadContract: O({
    caller: R('SourceLocation'), service_ref: Q(ID), runtime_binding_refs: ids,
    connection_key: Q(ID), database_source_ref: Q(ID), relation: Q(ID),
    lookup: A(O({ field: ID, op: ID, value_origin: S, evidence_refs: ids })),
    selected_fields: A(ID), transformations: A(S), failure_behavior: S,
    consistency_stage_refs: ids, evidence_refs: ids, unknowns: A(S)
  }),
  Observation: O({ id: ID, text: S, evidence_refs: { ...ids, minItems: 1 }, temporal_basis: E('current', 'historical', 'runtime', 'static', 'declared'), limitations: A(S) }),
  Interpretation: O({ id: ID, explanation: S, state: E('provisional', 'supported', 'weakened', 'unresolved'), support_refs: ids, counterevidence_refs: ids, unknowns: A(S), confidence_rationale: S }),
  Candidate: O({ entity_ref: ID, label: S, match_reason: S, evidence_refs: ids, ambiguity: A(S) }),
  Source: O({ source_ref: ID, kind: ID, label: S, environment: Q(ID), capabilities: ids, related_refs: ids, refreshed_at: Q(S), limitations: A(S) }),
  SourceItem: O({ item_ref: ID, kind: ID, summary: S, locator: S, event_time: Q(S), evidence_refs: ids }),
  Coverage: O({
    source_refs: ids, actual_scope: R('Scope'), query_description: S,
    complete_for_requested_scope: B, snapshot_refs: ids,
    freshness: O({ observed_at: S, watermark: Q(S), lag_ms: Q(I), index_updated_at: Q(S) }),
    sampling: Q(S), retention: Q(S), partial_reasons: A(S), pages_read: I,
    scanned_bytes: Q(I), scan_limit_reached: B
  }),
  ToolError: O({ code: ID, message: S, retryable: B, retry_after_ms: Q(I) }),
  ToolReceipt: O({
    call_ref: ID, tool: ID, status: E('ok', 'empty', 'partial', 'denied', 'not_found', 'unsupported', 'timeout', 'error'),
    data: { type: ['object', 'null'] }, evidence_refs: ids, coverage: R('Coverage'), next_cursor: Q(S),
    error: Q(R('ToolError')), cost: O({ elapsed_ms: I, backend_requests: I, bytes_scanned: Q(I) })
  }),
  TaskProposal: O({ agent_id: E(...investigators, 'D7', 'D8'), inquiry_kind: E('discovery', 'hypothesis_test', 'verification', 'report_draft', 'report_review'), question: S,
    known_premises: A(R('Premise')), exploratory_assumptions: A(S), unknowns: A(S), why_now: S, expected_information: S,
    scope: R('Scope'), dependency_versions: A(R('Dependency')), prerequisite_task_refs: ids, knowledge: R('Knowledge'), budget: R('Budget'), role_input: { type: 'object' } }),
  ReviewTarget: { ...O({ kind: E('claims', 'report'), claim_refs: ids, report_ref: Q(ID), report_hash: Q(ID), manifest_ref: ID, scope_revision: I }),
    allOf: [{ if: { properties: { kind: { const: 'report' } } }, then: { properties: { report_ref: ID, report_hash: ID } }, else: { properties: { claim_refs: { ...ids, minItems: 1 }, report_ref: { type: 'null' }, report_hash: { type: 'null' } } } }] },
  Section: O({ title: S, text: S, claim_refs: ids, evidence_refs: ids }),
  ReportContent: O({ diagnosis_status: E('cause_supported', 'cause_unresolved', 'complaint_unverified'), sections: A(R('Section')), claim_refs: ids, evidence_refs: ids, limitations: A(S), proposed_actions: A(O({ action: S, prerequisites: A(S), risks: A(S), evidence_refs: ids })) }),
};

export const roleInputs = {
  D1: O({ trigger: E('bootstrap', 'results', 'resume'), report_text: S, case_snapshot_ref: Q(ID), new_result_refs: ids }),
  D3: O({ search_terms: A(S), source_refs: ids, correlation_keys: A(R('CorrelationKey')), implementation_contract_refs: ids }),
  D4: O({ search_terms: A(S), repository_refs: ids, service_refs: ids, artifact_refs: ids, read_contract_refs: ids }),
  D5: O({ mode: E('discovery', 'read', 'history', 'diagnostics'), source_refs: ids, schema_refs: ids, read_contract_refs: ids, entity_keys: A(R('EntityKey')) }),
  D6: O({ search_terms: A(S), workflow_refs: ids, run_refs: ids, behavior_basis_refs: ids, implementation_contract_refs: ids }),
  D7: O({ target: R('ReviewTarget'), review_snapshot_ref: ID, supporting_refs: ids, contradicting_refs: ids, unresolved_questions: A(S) }),
  D8: O({ report_snapshot_ref: ID, requested_diagnosis_status: E('cause_supported', 'cause_unresolved', 'complaint_unverified'), claim_refs: ids, claim_review_refs: ids, output_format: E('incident_report'), supersedes_report_ref: Q(ID) }),
};

export const extensions = {
  D1: ['lead_decision', O({ action: E('delegate', 'clarify', 'request_review', 'request_report', 'deliver', 'stop_incomplete'),
    knowledge_delta: A(O({ text: S, kind: E('observation', 'assumption', 'unknown'), evidence_refs: ids })),
    hypothesis_updates: A(R('Interpretation')), dispatched_task_refs: ids, clarification_ref: Q(ID), report_ref: Q(ID), decision_reason: S, stop_reason: Q(S) })],
  D3: ['observed_execution', O({ candidate_attempts: A(R('Candidate')),
    boundaries: A(O({ stage: S, state: E('reached', 'explicit_failure', 'unknown'), correlation_basis: S, evidence_refs: ids })),
    cohort_comparisons: A(O({ description: S, denominator: Q(N), count: Q(N), count_semantics: E('exact', 'approximate', 'lower_bound', 'unknown'), evidence_refs: ids, limitations: A(S) })),
    timeline: A(O({ event_time: Q(S), ingestion_time: Q(S), description: S, evidence_refs: ids, ordering_limits: S })), outcome_semantics: A(S) })],
  D4: ['implementation_findings', O({ implementation_refs: A(R('SourceLocation')),
    runtime_bindings: A(O({ service_ref: ID, instance_ref: Q(ID), artifact_ref: Q(ID), source_revisions: ids, config_refs: ids, evidence_refs: ids, unknowns: A(S) })),
    behavior_contract: O({ summary: S, intended_behavior_refs: ids, read_contracts: A(R('ReadContract')), failure_branches: A(S), evidence_refs: ids }),
    connections: A(O({ from_ref: ID, to_ref: ID, kind: ID, basis: E('static', 'declared', 'runtime_observed'), evidence_refs: ids })), candidate_mechanisms: A(R('Interpretation')) })],
  D5: ['data_findings', O({ read_scope: O({ source_ref: Q(ID), schema_refs: ids, read_contract_refs: ids, entity_keys: A(R('EntityKey')), query_receipt_refs: ids }),
    values_or_diagnostics: A(O({ description: S, evidence_refs: ids, redacted: B })),
    temporal_basis: O({ current_state_only: B, historical_state_established: B, history_interval: Q(R('TimeRange')), freshness_receipt_refs: ids, limitations: A(S) }),
    consistency_path: A(O({ source_ref: ID, kind: E('database', 'replica', 'cache', 'index', 'transform'), evidence_refs: ids, unknowns: A(S) })),
    application_read_match: O({ status: E('verified', 'partial', 'unknown', 'mismatch'), explanation: S, evidence_refs: ids, unknowns: A(S) }) })],
  D6: ['ai_findings', O({ run_scope: O({ workflow_refs: ids, run_refs: ids, step_refs: ids, version_refs: ids }),
    behavior_basis: O({ description: S, evidence_refs: ids, assumptions: A(S) }),
    stage_observations: A(O({ stage_ref: ID, input_refs: ids, output_refs: ids, evidence_refs: ids, limitations: A(S) })),
    divergence: A(O({ description: S, expected_refs: ids, observed_refs: ids, unknowns: A(S) })), candidate_mechanisms: A(R('Interpretation')) })],
  D7: ['review', O({ target: R('ReviewTarget'), verdict: E('accept', 'revise', 'insufficient', 'failed'), accepted_scope: A(S),
    objections: A(O({ text: S, affected_refs: ids, evidence_refs: ids })), required_followups: A(R('Followup')), limitations: A(S) })],
  D8: ['report_draft', O({ report_ref: Q(ID), report_version: Q(I), diagnosis_status: E('cause_supported', 'cause_unresolved', 'complaint_unverified'),
    content: R('ReportContent'), dependency_manifest_ref: Q(ID), issues_for_D1: A(S) })],
};

export const commonTask = {
  protocol_version: { const: '1' }, case_id: ID, task_id: ID, attempt_id: ID, case_revision: I, scope_revision: I,
  inquiry_kind: E('discovery', 'hypothesis_test', 'verification', 'report_draft', 'report_review'), question: S,
  known_premises: A(R('Premise')), exploratory_assumptions: A(S), unknowns: A(S), why_now: S, expected_information: S,
  scope: R('Scope'), dependency_versions: A(R('Dependency')), prerequisite_task_refs: ids, knowledge: R('Knowledge'), budget: R('Budget'), output_contract: { const: 'AgentAnswer-v1' },
};
export const commonAnswer = {
  execution_status: E('complete', 'partial', 'failed', 'cancelled'), observations: A(R('Observation')), interpretations: A(R('Interpretation')),
  unknowns: A(S), coverage_receipt_refs: ids, suggested_followups: A(R('Followup')),
};
const root = (title, schema) => ({ $schema: 'https://json-schema.org/draft/2020-12/schema', title, ...schema, $defs: defs });
const taskVariants = AGENTS.map(id => O({ ...commonTask, agent_id: { const: id }, role_input: roleInputs[id] }));
const answerVariants = AGENTS.map(id => O({ agent_id: { const: id }, ...commonAnswer, [extensions[id][0]]: extensions[id][1] }));
export const agentSchema = root('Proposed incident-agent interfaces', {
  oneOf: [R('Task'), R('AgentAnswer'), R('Result')],
});
Object.assign(agentSchema.$defs, {
  Task: { oneOf: taskVariants }, AgentAnswer: { oneOf: answerVariants },
  Result: { ...O({ protocol_version: { const: '1' }, result_id: ID, case_id: ID, task_id: ID, attempt_id: ID, agent_id: E(...AGENTS), case_revision: I, scope_revision: I,
    dependency_versions: A(R('Dependency')), answer_state: E('valid', 'unavailable', 'invalid', 'cancelled'), answer: Q(R('AgentAnswer')), tool_receipt_refs: ids, errors: A(R('ToolError')),
    cost: O({ elapsed_ms: I, tool_calls: I, model_calls: I, input_tokens: Q(I), output_tokens: Q(I), backend_scanned_bytes: Q(I) }) }),
    allOf: [{ if: { properties: { answer_state: { const: 'valid' } } }, then: { properties: { answer: R('AgentAnswer') } }, else: { properties: { answer: { type: 'null' } } } }] },
});

// Each operation has a strict input schema and a success/partial data schema.
// ToolReceipt is the common response wrapper. All evidence/cost/coverage is connector-owned.
export const tools = [];
function T(name, agents, backend, purpose, input, output, constraints) {
  tools.push({ name, agents, backend, purpose, constraints, input_schema: O({ ...input, limits: R('ToolLimits') }), data_schema: O(output) });
}
const page = { cursor: Q(S) };
const evidence = { evidence_refs: ids };
const sourceRef = { source_ref: ID };
T('catalog.search', sourceReaders, 'Configured source/service directory', 'Find candidate sources/services/repos by feature terms; does not establish the failing component.',
  { query: S, kinds: A(E('service', 'repository', 'database', 'replica', 'telemetry', 'deployment', 'configuration', 'ai_workflow', 'history', 'cache', 'index')), ...page }, { candidates: A(R('Source')) }, 'Authorization filters metadata before return; bounded indexed discovery, not raw estate scanning.');
T('catalog.describe', sourceReaders, 'Configured source/service directory', 'Describe one discovered source, capabilities, relationships and freshness.',
  { entity_ref: ID }, { source: R('Source'), relationships: A(O({ from_ref: ID, to_ref: ID, kind: ID, basis: E('declared', 'indexed', 'runtime_observed'), evidence_refs: ids })) }, 'Declared relationships are leads, not automatically runtime truth.');
T('history.search', ['D1', 'D7'], 'Authorized runbook/contract/past-incident index', 'Retrieve useful precedent or intended-behavior documents.',
  { query: S, entity_refs: ids, ...page }, { items: A(R('SourceItem')) }, 'No ground-truth labels or future fixes from held-out evaluation cases; precedent is not current causal proof.');
T('case.read', AGENTS, 'Investigator-owned case store', 'Read a bounded current, review or report snapshot and its references.',
  { view: E('current', 'review', 'report'), snapshot_ref: Q(ID), sections: A(E('scope', 'claims', 'hypotheses', 'results', 'unknowns', 'coverage', 'reviews', 'reports', 'read_contracts')) },
  { snapshot_ref: ID, case_revision: I, scope_revision: I, artifact_refs: ids, excerpts: A(R('Excerpt')) }, 'D8 restricted to assigned report snapshot; D7 gets independent review snapshot.');
T('evidence.fetch', AGENTS, 'Evidence registry plus authorized original-source fetch', 'Fetch cited original excerpts or accepted shared artifacts, including code-to-data read contracts.',
  { refs: ids, selectors: A(S) }, { excerpts: A(R('Excerpt')), read_contracts: A(R('ReadContract')), artifact_refs: ids }, 'Recheck access on every fetch; selectors/ranges are bounded, secrets redacted, no unrestricted URL fetch.');
T('delegate_task', ['D1'], 'Investigator task runtime', 'Validate a task proposal, reserve budget and enqueue it once; runtime assigns IDs/revisions.',
  { idempotency_key: ID, proposal: R('TaskProposal') }, { task_ref: ID, state: E('queued', 'waiting_prerequisites', 'existing'), effective_budget: R('Budget') }, 'Validate role_input against target Task schema; clamp limits, check prerequisites and review gates; same key returns same task.');
T('request_clarification', ['D1'], 'Investigator UI/request channel', 'Record and present a focused missing-scope question to the user.',
  { question: S, candidate_refs: ids, why_needed: S }, { clarification_ref: ID, state: E('pending', 'answered'), answer: Q(S) }, 'Pending means no user answer yet; agent cannot manufacture one or keep investigating an arbitrarily chosen candidate.');

T('telemetry.describe_sources', ['D3', 'D7'], 'Configured telemetry source metadata APIs', 'Inspect queryable fields, retention, sampling and supported correlation/status operations.',
  { source_refs: ids }, { sources: A(O({ source_ref: ID, fields: A(ID), operations: ids, retention: Q(S), sampling: Q(S), limitations: A(S) })) }, 'No implied cloud integration when the source/operation is unconfigured.');
T('telemetry.aggregate', ['D3', 'D7'], 'Actual log/metric/event backend', 'Run bounded counts/rates/distributions to narrow time, service or cohort.',
  { ...sourceRef, time_range: R('TimeRange'), filters: A(filter), group_by: A(ID), measure: E('count', 'error_rate', 'latency'), ...page },
  { groups: A(O({ keys: A(R('EntityKey')), value: N, unit: E('count', 'ratio', 'milliseconds'), denominator: Q(N), semantics: E('exact', 'approximate', 'lower_bound') })) }, 'Validate fields and denominator/units; scan caps plus page caps; no arbitrary backend query language.');
T('telemetry.query_events', ['D3', 'D7'], 'Actual configured logs/events store', 'Fetch relevant original log/event records using validated terms, IDs and filters.',
  { ...sourceRef, time_range: R('TimeRange'), search_terms: A(S), filters: A(filter), ...page }, { events: A(R('SourceItem')) }, 'Distinguish event/ingestion time; query exhaustion is not proof of absent execution.');
T('telemetry.fetch_trace', ['D3', 'D7'], 'Tracing backend', 'Read a specific trace and bounded span summaries/links.',
  { ...sourceRef, trace_id: ID, ...page }, { trace_id: ID, spans: A(O({ span_ref: ID, parent_ref: Q(ID), links: ids, service_ref: Q(ID), operation: S, status: S, evidence_refs: ids })) }, 'Trace sampling/partial retention exposed; async work need not share a single trace.');
T('telemetry.correlate_messages', ['D3', 'D7'], 'Configured message/job correlation indexes', 'Find records joined through discovered request/job/message/run keys.',
  { source_refs: ids, keys: A(R('CorrelationKey')), time_range: R('TimeRange'), ...page }, { links: A(O({ from_ref: ID, to_ref: ID, key: R('CorrelationKey'), certainty: E('exact_key', 'candidate'), evidence_refs: ids })) }, 'Time proximity alone cannot become an exact join.');
T('telemetry.read_status', ['D3', 'D7'], 'Queue/worker/provider read-only APIs', 'Read a discovered queue backlog, worker state or message delivery receipt.',
  { ...sourceRef, kind: E('queue', 'worker', 'provider_message'), entity_ref: ID }, { items: A(O({ entity_ref: ID, status: S, meaning: S, observed_at: S, evidence_refs: ids })) }, 'Provider acceptance, delivery and user visibility are separate meanings; no sends/retries/queue mutations.');

T('code.search', ['D4', 'D7'], 'Read-only checkouts or version-aware code index', 'Locate candidate paths, text matches or symbols across authorized repositories.',
  { repository_refs: ids, revision: Q(ID), kind: E('paths', 'text', 'symbols'), query: S, ...page },
  { matches: A(O({ location: R('SourceLocation'), excerpt: S, match_kind: E('path', 'text', 'symbol'), navigation_basis: E('text', 'indexed_symbol'), limitations: A(S) })) }, 'Empty repo list means bounded authorized catalog/index discovery only; never an unlimited raw clone/scan. Revision null permits discovery, not deployed attribution.');
T('code.read_at_revision', ['D4', 'D7'], 'Repository API or immutable checkout', 'Read an exact versioned file range; no execution of its code.',
  { repository_ref: ID, commit: ID, path: ID, start_line: { type: 'integer', minimum: 1 }, end_line: { type: 'integer', minimum: 1 } }, { location: R('SourceLocation'), content: S }, 'Require resolved immutable commit, validated path containment, line/byte caps and secret redaction. No silent latest-branch fallback.');
T('code.references', ['D4', 'D7'], 'Language/symbol indexes with text fallback', 'Find definitions, callers or references to a discovered symbol.',
  { location: R('SourceLocation'), symbol: ID, direction: E('definition', 'callers', 'references'), ...page }, { matches: A(O({ location: R('SourceLocation'), basis: E('precise_index', 'text_candidate'), excerpt: S })) }, 'Mark unresolved dynamic dispatch/cross-repo index gaps; static references do not prove actual calls.');
T('code.diff', ['D4', 'D7'], 'Repository version-control API/index', 'Compare two discovered immutable source revisions.',
  { repository_ref: ID, base_commit: ID, head_commit: ID, paths: A(ID), ...page }, { changes: A(O({ path: ID, patch_excerpt: S, evidence_refs: ids })) }, 'A recent change is a candidate, not automatically the cause.');
T('build.provenance', ['D4', 'D7'], 'CI/artifact provenance store', 'Resolve a built artifact to recorded source inputs and build identity.',
  { artifact_ref: ID }, { artifact_ref: ID, source_locations: A(R('SourceLocation')), build_ref: Q(ID), verification: E('verified_record', 'unverified_record', 'unavailable'), ...evidence }, 'One artifact may have multiple repository inputs; provenance presence is not deployed activation.');
T('deploy.history', ['D4', 'D7'], 'Configured CI/CD/cloud/container deployment API', 'Read releases, failed rollouts and placement changes in a bounded interval.',
  { service_ref: ID, environment: ID, time_range: R('TimeRange'), ...page }, { deployments: A(O({ deployment_ref: ID, service_ref: ID, artifact_ref: Q(ID), status: S, changed_at: S, evidence_refs: ids })) }, 'Read-only metadata; failed deployment may never have served traffic.');
T('deploy.instance_binding', ['D4', 'D7'], 'Runtime instance inventory and release records', 'Bind the affected instance/attempt time to artifact/config where recorded.',
  { service_ref: ID, environment: ID, instance_ref: Q(ID), event_time: S }, { bindings: A(O({ instance_ref: Q(ID), artifact_ref: Q(ID), config_refs: ids, interval: Q(R('TimeRange')), evidence_refs: ids, unknowns: A(S) })) }, 'Preserve mixed rollout cohorts and missing historical records; do not infer a shared SHA.');
T('config.effective', ['D4', 'D7'], 'Read-only effective configuration/feature-flag metadata', 'Inspect effective nonsecret settings, connection identities and secret-version metadata.',
  { service_ref: ID, environment: ID, instance_ref: Q(ID), keys: A(ID), event_time: Q(S) }, { settings: A(O({ key: ID, value: scalar, redacted: B, version_ref: Q(ID), effective_at: Q(S), related_source_ref: Q(ID), evidence_refs: ids })) }, 'Historical lookup only if backend supports it; connection identity may be returned, credential values must not.');
T('config.history', ['D4', 'D7'], 'Retained configuration/flag audit store', 'Read recorded setting changes and effective intervals.',
  { service_ref: ID, environment: ID, keys: A(ID), time_range: R('TimeRange'), ...page }, { changes: A(R('SourceItem')) }, 'No current-value substitution for missing historical config.');
T('infra.inspect', ['D4', 'D7'], 'Authorized read-only cloud/container/network/IAM APIs', 'Inspect a discovered infrastructure resource or policy for a bounded question.',
  { resource_ref: ID, kind: E('runtime', 'network', 'permission', 'storage'), question: S, event_time: Q(S) }, { findings: A(O({ condition: S, observed_at: S, evidence_refs: ids, limitations: A(S) })) }, 'No active network experiments, command execution, restarts or permission changes. Historical state may be unavailable.');

T('data.describe_source', ['D4', 'D5', 'D7'], 'Configured database/data-source directory and read-only metadata', 'Resolve database identity, replica relationship, query/history support and freshness.',
  { ...sourceRef }, { source: R('Source'), primary_identity_ref: Q(ID), replica: B, schema_search_supported: B, history_source_refs: ids, replay_watermark: Q(S), lag_ms: Q(I) }, 'No privileged connection string is returned. An unavailable replica is not permission to query primary.');
T('data.inspect_schema', ['D4', 'D5', 'D7'], 'Approved replica/catalog metadata', 'Search permitted relation/column metadata or describe a discovered relation.',
  { ...sourceRef, query: S, relation: Q(ID), ...page }, { schema_ref: ID, relations: A(O({ relation: ID, kind: E('table', 'view', 'materialized_view'), columns: A(O({ name: ID, type: ID, nullable: B })), keys: A(A(ID)), relationships: A(S), evidence_refs: ids })) }, 'Bounded metadata search; relation names alone do not establish application usage.');
T('data.read_bounded', ['D5', 'D7'], 'Approved read-replica connector', 'Execute a validated parameterized read or an approved read template.',
  { ...sourceRef, schema_ref: ID, read_contract_ref: Q(ID), relation: ID, columns: A(ID), filters: A(filter), order_by: A(O({ field: ID, direction: E('asc', 'desc') })), query_template_ref: Q(ID), template_parameters: A(R('EntityKey')), ...page },
  { columns: A(O({ name: ID, type: ID, redacted: B })), rows: A(A(R('JsonValue'))), query_ref: ID, query_observed_at: S, replay_watermark: Q(S), lag_ms: Q(I) }, 'Current-state read only. Backend validates identifiers/operators, tenant restrictions, template semantics and cost. No arbitrary SQL/functions or primary fallback; rows follow column order.');
T('data.history', ['D5', 'D7'], 'Actual configured audit/CDC/versioned history source', 'Read retained changes/historical values for an established data scope.',
  { history_source_ref: ID, read_contract_ref: Q(ID), relation: ID, entity_keys: A(R('EntityKey')), fields: A(ID), time_range: R('TimeRange'), ...page },
  { changes: A(O({ valid_from: Q(S), valid_to: Q(S), fields: A(R('EntityKey')), transaction_ref: Q(ID), evidence_refs: ids })), historical_state_established: B, limitations: A(S) }, 'Audit completeness/ordering must support the claimed interval; a plain replica cannot time-travel. Unsupported history remains unknown.');
T('data.lineage', ['D5', 'D7'], 'Registered data lineage and retained transform records', 'Find established views, transformations, replica/cache/index relationships.',
  { ...sourceRef, relation: ID, direction: E('upstream', 'downstream'), ...page }, { links: A(O({ from_ref: ID, to_ref: ID, transformation: S, basis: E('declared', 'implementation', 'runtime_observed'), evidence_refs: ids })) }, 'Declared lineage is not proof the failing run followed it.');
T('data.diagnostics', ['D5', 'D7'], 'Approved read-only database monitoring interface', 'Read available query-plan metadata/statistics, locks, connection or replication health.',
  { ...sourceRef, kind: E('plan', 'statistics', 'locks', 'connections', 'replication'), query_ref: Q(ID), time_range: Q(R('TimeRange')) },
  { findings: A(O({ metric: ID, value: scalar, unit: Q(S), observed_at: S, evidence_refs: ids, limitations: A(S) })) }, 'Plan inspection cannot use executing ANALYZE or unsafe functions. Primary-only facts need separately approved monitoring, not a privileged DB session.');
T('data.read_cache_index', ['D5', 'D7'], 'Discovered cache/search-index read connector', 'Read narrowly identified cache entries or indexed documents and version/TTL metadata.',
  { ...sourceRef, read_contract_ref: Q(ID), key_refs: ids, ...page }, { items: A(O({ key_ref: ID, fields: A(R('EntityKey')), version_ref: Q(ID), expires_at: Q(S), evidence_refs: ids })) }, 'Source must first exist in authorized metadata/evidence; no cache presumed, no invalidation/reindex/write.');

T('ai.list_workflows', ['D6', 'D7'], 'Configured AI workflow/run directory', 'Discover candidate application workflows by feature terms.',
  { query: S, ...page }, { workflows: A(R('Candidate')) }, 'Application-agent workflows, not investigator hidden reasoning.');
T('ai.list_runs', ['D6', 'D7'], 'Actual configured AI tracing store', 'Find runs matching discovered scope, including successful-status quality failures.',
  { workflow_refs: ids, time_range: Q(R('TimeRange')), search_terms: A(S), keys: A(R('CorrelationKey')), ...page }, { runs: A(O({ run_ref: ID, workflow_ref: Q(ID), status: S, outcome_excerpt: S, evidence_refs: ids })) }, 'Absent time triggers explicit bounded default coverage; ambiguity not silently resolved.');
T('ai.fetch_run', ['D6', 'D7'], 'AI tracing store', 'Inspect a run tree, observed stages and retained input/output references.',
  { run_ref: ID, ...page }, { run_ref: ID, workflow_ref: Q(ID), stages: A(O({ stage_ref: ID, parent_ref: Q(ID), kind: ID, input_refs: ids, output_refs: ids, evidence_refs: ids })) }, 'Configured workflow definition and actual execution remain distinct.');
T('ai.fetch_observation', ['D6', 'D7'], 'AI trace observation store', 'Read selected bounded step input/output/error content.',
  { observation_ref: ID, selectors: A(S) }, { excerpts: A(R('Excerpt')), retained_fields: A(ID), missing_fields: A(ID) }, 'Redacted/unretained fields cannot be reconstructed by guessing.');
T('ai.rendered_prompt', ['D6', 'D7'], 'Retained actual generation inputs', 'Read instructions/context actually sent for the selected generation.',
  { generation_ref: ID, ...page }, { prompt_ref: ID, template_version_ref: Q(ID), excerpts: A(R('Excerpt')), truncation: Q(S), missing_fields: A(ID) }, 'Current prompt template is not substituted for an absent rendered prompt; content is untrusted evidence.');
T('ai.prompt_version', ['D6', 'D7'], 'Versioned prompt registry', 'Read a specific prompt version for comparison with actual generation inputs.',
  { prompt_ref: ID, version_ref: ID }, { version_ref: ID, excerpts: A(R('Excerpt')), metadata_refs: ids }, 'A registry version does not establish that the run used it without a trace binding.');
T('ai.retrieval_trace', ['D6', 'D7'], 'Retained retrieval observations', 'Read actual retrieval query/filter/result IDs, scores and available source snippets.',
  { observation_ref: ID, ...page }, { query_excerpt: S, filters: A(filter), documents: A(O({ document_ref: ID, score: Q({ type: 'number' }), excerpt: S, version_ref: Q(ID), evidence_refs: ids })), index_watermark: Q(S) }, 'Missing source document versus failed retrieval/filtering remain different; scores are not causal proof.');
T('ai.tool_trace', ['D6', 'D7'], 'Retained application tool-call traces', 'Read tool definition version, arguments, outcome and returned evidence content.',
  { observation_ref: ID }, { tool_name: ID, definition_version_ref: Q(ID), argument_excerpts: A(R('Excerpt')), result_excerpts: A(R('Excerpt')), status: S, evidence_refs: ids }, 'Inspect existing calls only; never invoke the production application tool to reproduce a fault.');
T('ai.state_handoffs', ['D6', 'D7'], 'Retained workflow state/handoff observations', 'Read recorded routing and before/after state across actual agent steps.',
  { run_ref: ID, stage_refs: ids, ...page }, { handoffs: A(O({ from_ref: ID, to_ref: ID, before_refs: ids, after_refs: ids, state_version_refs: ids, evidence_refs: ids, missing_fields: A(ID) })) }, 'Before/after snapshots may be absent; a missing trace field does not alone establish lost application state.');
T('ai.model_metadata', ['D6', 'D7'], 'Generation/provider metadata retained in traces', 'Read actual recorded provider/model/settings/finish metadata.',
  { generation_ref: ID }, { provider: Q(ID), model: Q(ID), version_ref: Q(ID), settings: A(R('EntityKey')), finish_reason: Q(S), evidence_refs: ids, unavailable: A(ID) }, 'Hidden provider versions/internal reasoning remain unavailable, not fabricated.');

T('report.store_draft', ['D8'], 'Investigator-owned immutable artifact store', 'Validate and store structured report content; runtime canonicalizes bytes, computes hash and binds dependencies.',
  { idempotency_key: ID, report_snapshot_ref: ID, content: R('ReportContent'), supersedes_report_ref: Q(ID) },
  { report_ref: ID, report_version: I, artifact_hash: ID, dependency_manifest_ref: ID, approval_state: { const: 'unreviewed' } }, 'No writer self-approval. Stored content must match submitted structured content; source/claim refs validated, exact artifact goes to D7.');

export const toolSchema = root('Proposed tool contracts', R('ToolReceipt'));
export function schemaFor(name) { return root(name, R(name)); }
