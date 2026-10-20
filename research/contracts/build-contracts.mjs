import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { AGENTS, defs, tools, agentSchema, toolSchema, commonTask, commonAnswer, roleInputs, extensions, O, R } from './definitions.mjs';

// Generated artifacts only. Edit definitions.mjs and this synthetic fixture source.
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);
const write = (name, value) => fs.writeFileSync(path.join(here, name), JSON.stringify(value, null, 2) + '\n');
const emptyScope = { entity_refs: [], feature_terms: ['customer group messaging'], environment: null, time_range: null, repository_refs: [] };
const scope = { ...emptyScope, entity_refs: ['service:delivery', 'customer:G42'], environment: 'production', time_range: { start: '2026-10-20T10:25:00Z', end: '2026-10-20T10:40:00Z', basis: 'event' }, repository_refs: ['repo:delivery'] };
const location = { repository_ref: 'repo:delivery', commit: 'fixture-commit-r18', path: 'src/delivery.ts', start_line: 40, end_line: 66, evidence_refs: ['E3'] };
const readContract = {
  caller: location, service_ref: 'service:delivery', runtime_binding_refs: ['E3B'], connection_key: 'MESSAGING_DB', database_source_ref: 'db:messaging', relation: 'messaging.group_routes',
  lookup: [{ field: 'customer_id', op: 'eq', value_origin: 'delivery job.customer_id', evidence_refs: ['E3'] }, { field: 'active', op: 'eq', value_origin: 'literal true', evidence_refs: ['E3'] }],
  selected_fields: ['legacy_destination_id'], transformations: [], failure_behavior: 'Empty legacy_destination_id causes recipient_missing before provider send.', consistency_stage_refs: [], evidence_refs: ['E3'], unknowns: ['Incident-time row values; actual reader consistency context.']
};
const entityKey = { field: 'customer_id', value: 'G42', evidence_refs: ['E1'] };
const target = { kind: 'claims', claim_refs: ['C2@1'], report_ref: null, report_hash: null, manifest_ref: 'manifest:C2@1', scope_revision: 2 };
const explanation = { id: 'H1', explanation: 'Missing or incompatible destination representation may explain the lookup failure.', state: 'provisional', support_refs: ['E1', 'E3'], counterevidence_refs: [], unknowns: ['Incident-time data'], confidence_rationale: 'Implementation and failure stage align; historical data has not been established.' };
const followup = { agent_id: 'D5', question: 'Establish incident-time values for the discovered lookup scope, or retain the gap.', premise_refs: ['E1', 'E3', 'RC1'], unknowns: ['Historical row values'], expected_information: 'Time-matched fields and source-history coverage.' };
const content = {
  diagnosis_status: 'cause_unresolved',
  sections: [
    { title: 'Observed issue', text: 'For M17, recipient resolution recorded a terminal failure before a provider send.', claim_refs: ['C1@1'], evidence_refs: ['E1', 'E4'] },
    { title: 'Implemented versus observed', text: 'The bound implementation reads legacy_destination_id and stops when empty. M17 recorded an empty result and stopped.', claim_refs: ['C2@1'], evidence_refs: ['E3', 'E3B', 'E4'] },
    { title: 'Cause remains unresolved', text: 'Current row values do not establish what data the worker could read at incident time.', claim_refs: ['C3@1'], evidence_refs: ['E2'] }
  ], claim_refs: ['C1@1', 'C2@1', 'C3@1'], evidence_refs: ['E1', 'E2', 'E3', 'E3B', 'E4'],
  limitations: ['No time-matched row history is available in this fixture; broader customer impact is unverified.'],
  proposed_actions: [{ action: 'Obtain time-matched row/read evidence before promoting a data or compatibility explanation.', prerequisites: ['Authorized history source or retained application read records'], risks: ['A current-state query cannot substitute for historical evidence.'], evidence_refs: ['E2', 'E3'] }]
};
const inputs = {
  D1: { trigger: 'bootstrap', report_text: 'The customer group did not receive the message.', case_snapshot_ref: null, new_result_refs: [] },
  D3: { search_terms: ['customer group', 'delivery'], source_refs: ['logs:delivery-prod'], correlation_keys: [], implementation_contract_refs: [] },
  D4: { search_terms: ['recipient resolution', 'recipient_missing'], repository_refs: ['repo:delivery'], service_refs: ['service:delivery'], artifact_refs: [], read_contract_refs: [] },
  D5: { mode: 'history', source_refs: ['db:messaging-replica'], schema_refs: [], read_contract_refs: ['RC1'], entity_keys: [entityKey] },
  D6: { search_terms: ['order assistant', 'wrong answer'], workflow_refs: ['workflow:order-assistant'], run_refs: ['run:17'], behavior_basis_refs: ['E6'], implementation_contract_refs: [] },
  D7: { target, review_snapshot_ref: 'snapshot:review-4', supporting_refs: ['E1', 'E3', 'E4'], contradicting_refs: [], unresolved_questions: ['Incident-time row values'] },
  D8: { report_snapshot_ref: 'snapshot:report-4', requested_diagnosis_status: 'cause_unresolved', claim_refs: content.claim_refs, claim_review_refs: ['review:C1', 'review:C2', 'review:C3'], output_format: 'incident_report', supersedes_report_ref: null }
};
const questions = {
  D1: 'Discover which incident the complaint refers to and choose useful next questions.',
  D3: 'Locate matching delivery attempts and recorded stages; report ambiguity and coverage.',
  D4: 'Explain the failing recipient-resolution stage and its deployed binding; discover its data dependencies.',
  D5: 'Using RC1 and its cited code, establish the relevant row values at incident time; distinguish current from historical evidence.',
  D6: 'Inspect the observed wrong-answer run, actual lookup output and next-step input; locate supported divergence.',
  D7: 'Review the scoped lookup explanation and challenge missing causal prerequisites.',
  D8: 'Draft a concise cause-unresolved report from the assigned snapshot and cited findings; do not invent the missing history.'
};
const outputs = {
  D1: { action: 'delegate', knowledge_delta: [{ text: 'Catalog search returned a candidate delivery service, not a confirmed incident match.', kind: 'observation', evidence_refs: ['E0'] }], hypothesis_updates: [], dispatched_task_refs: ['task:D3-discovery'], clarification_ref: null, report_ref: null, decision_reason: 'Investigate matching attempts before naming a failing component or cause.', stop_reason: null },
  D3: { candidate_attempts: [{ entity_ref: 'attempt:M17', label: 'Candidate group delivery', match_reason: 'Recorded delivery for the matched customer/time.', evidence_refs: ['E1'], ambiguity: [] }], boundaries: [{ stage: 'recipient_resolution', state: 'explicit_failure', correlation_basis: 'Same discovered message/job identifier', evidence_refs: ['E1'] }], cohort_comparisons: [], timeline: [{ event_time: '2026-10-20T10:32:00Z', ingestion_time: null, description: 'Terminal recipient_missing', evidence_refs: ['E1'], ordering_limits: 'No full upstream trace established.' }], outcome_semantics: ['This establishes a local failure, not its underlying cause.'] },
  D4: { implementation_refs: [location], runtime_bindings: [{ service_ref: 'service:delivery', instance_ref: 'instance:W', artifact_ref: 'artifact:r18', source_revisions: ['fixture-commit-r18'], config_refs: ['config:W'], evidence_refs: ['E3B'], unknowns: [] }], behavior_contract: { summary: 'Read the active customer route; abort before send if legacy destination is empty.', intended_behavior_refs: [], read_contracts: [readContract], failure_branches: ['recipient_missing on empty legacy_destination_id'], evidence_refs: ['E3'] }, connections: [{ from_ref: 'service:delivery', to_ref: 'db:messaging', kind: 'database_read', basis: 'static', evidence_refs: ['E3'] }], candidate_mechanisms: [explanation] },
  D5: { read_scope: { source_ref: 'db:messaging-replica', schema_refs: ['schema:routes-v1'], read_contract_refs: ['RC1'], entity_keys: [entityKey], query_receipt_refs: ['call:D5-read'] }, values_or_diagnostics: [{ description: 'Current row has destination_id=chat-7 and legacy_destination_id=null.', evidence_refs: ['E2'], redacted: false }], temporal_basis: { current_state_only: true, historical_state_established: false, history_interval: null, freshness_receipt_refs: ['call:D5-read'], limitations: ['No configured audit source for the requested interval; replica replay watermark unknown.'] }, consistency_path: [{ source_ref: 'db:messaging-replica', kind: 'replica', evidence_refs: ['E2'], unknowns: ['Freshness and actual application read snapshot at incident time.'] }], application_read_match: { status: 'partial', explanation: 'Current schema supports the code lookup; incident-time visibility is unverified.', evidence_refs: ['E2', 'E3'], unknowns: ['Values visible to the worker at 10:32.'] } },
  D6: { run_scope: { workflow_refs: ['workflow:order-assistant'], run_refs: ['run:17'], step_refs: ['step:lookup', 'step:answer'], version_refs: [] }, behavior_basis: { description: 'The task was to answer using the returned order.', evidence_refs: ['E6'], assumptions: [] }, stage_observations: [{ stage_ref: 'step:lookup', input_refs: ['E7-in'], output_refs: ['E7-out'], evidence_refs: ['E7'], limitations: [] }, { stage_ref: 'step:answer', input_refs: ['E8-in'], output_refs: ['E8-out'], evidence_refs: ['E8'], limitations: [] }], divergence: [{ description: 'A returned order field is absent from the retained next-step input.', expected_refs: ['E6', 'E7-out'], observed_refs: ['E8-in'], unknowns: ['Whether the transformation or trace retention omitted it.'] }], candidate_mechanisms: [] },
  D7: { target, verdict: 'insufficient', accepted_scope: ['The inspected deployed lookup failed for M17.'], objections: [{ text: 'Current E2 values cannot establish incident-time data or prove a compatibility cause.', affected_refs: ['C2@1', 'H1'], evidence_refs: ['E2', 'E3'] }], required_followups: [followup], limitations: ['Incident-time row history is unavailable so far.'] },
  D8: { report_ref: 'report:I17-v1', report_version: 1, diagnosis_status: 'cause_unresolved', content, dependency_manifest_ref: 'manifest:report-I17-v1', issues_for_D1: [] }
};
const observations = {
  D1: ['Catalog returned a candidate delivery service.', ['E0'], 'declared'],
  D3: ['M17 recorded recipient-resolution failure.', ['E1'], 'runtime'],
  D4: ['The inspected source reads legacy_destination_id.', ['E3'], 'static'],
  D5: ['The scoped current row has an empty legacy destination.', ['E2'], 'current'],
  D6: ['Retained lookup output and next-step input differ in one order field.', ['E7', 'E8'], 'runtime'],
  D7: ['E2 is a current-state query, not historical row evidence.', ['E2'], 'current'],
  D8: ['The report snapshot supports a localized failure but retains the causal gap.', ['E1', 'E3', 'E4'], 'runtime']
};
const fixtures = AGENTS.map((agent, index) => {
  const bootstrap = agent === 'D1';
  const task = {
    protocol_version: '1', case_id: 'I17', task_id: `T-${agent}`, attempt_id: `T-${agent}-A1`, agent_id: agent,
    case_revision: bootstrap ? 0 : 4, scope_revision: bootstrap ? 0 : 2,
    inquiry_kind: agent === 'D8' ? 'report_draft' : agent === 'D7' ? 'verification' : ['D1', 'D3', 'D4'].includes(agent) ? 'discovery' : 'hypothesis_test',
    question: questions[agent], known_premises: bootstrap ? [] : agent === 'D6' ? [{ claim_ref: 'C-AI1@1', evidence_refs: ['E6'] }] : [{ claim_ref: 'C1@1', evidence_refs: ['E1'] }],
    exploratory_assumptions: [], unknowns: bootstrap ? ['Affected customer, event time, service and actual symptom.'] : agent === 'D6' ? ['Whether an application transformation lost the field or trace retention omitted it.'] : ['Incident-time data and causal attribution.'],
    why_now: bootstrap ? 'New unverified complaint.' : 'The current case snapshot establishes the prerequisite for this scoped question.', expected_information: questions[agent],
    scope: bootstrap ? emptyScope : agent === 'D6' ? { ...scope, entity_refs: ['workflow:order-assistant', 'run:17'], feature_terms: ['order assistant wrong answer'], repository_refs: [] } : scope, dependency_versions: bootstrap ? [] : [{ ref: agent === 'D6' ? 'C-AI1' : 'C1', version: '1' }], prerequisite_task_refs: [],
    knowledge: { brief: bootstrap ? 'Only the complaint is known. No service/table/cause is established.' : 'Use cited originals; the failure stage is localized, while the underlying cause remains unresolved.', artifact_refs: bootstrap ? [] : ['snapshot:case-4'], excerpts: agent === 'D5' ? [{ evidence_ref: 'E3', locator: 'repo:delivery@fixture-commit-r18:src/delivery.ts:40-66', text: 'Read active group_routes by customer_id; use legacy_destination_id; stop on empty.' }] : [], read_contract_refs: agent === 'D5' ? ['RC1'] : [] },
    budget: { tool_calls_max: 8, wall_ms_max: 60000, model_tokens_max: 12000, output_tokens_max: 2500 }, output_contract: 'AgentAnswer-v1', role_input: inputs[agent]
  };
  const [text, evidence_refs, temporal_basis] = observations[agent];
  const answer = {
    agent_id: agent, execution_status: agent === 'D5' ? 'partial' : 'complete',
    observations: [{ id: `O-${agent}-1`, text, evidence_refs, temporal_basis, limitations: [] }], interpretations: [],
    unknowns: agent === 'D1' ? ['Correct incident match.'] : agent === 'D6' ? ['Actual transformation behavior versus retained trace coverage.'] : ['Incident-time data; broader impact.'], coverage_receipt_refs: [`call:${agent}-fixture`],
    suggested_followups: agent === 'D4' ? [followup] : [], [extensions[agent][0]]: outputs[agent]
  };
  return { description: 'Synthetic teaching fixture. Evidence IDs/content are invented and must not enter a real case. Not a fixed agent execution order.', task, answer,
    result: { protocol_version: '1', result_id: `result:${agent}-fixture`, case_id: task.case_id, task_id: task.task_id, attempt_id: task.attempt_id, agent_id: agent,
      case_revision: task.case_revision, scope_revision: task.scope_revision, dependency_versions: task.dependency_versions, answer_state: 'valid', answer, tool_receipt_refs: answer.coverage_receipt_refs,
      errors: [], cost: { elapsed_ms: 100 + index, tool_calls: 1, model_calls: 2, input_tokens: null, output_tokens: null, backend_scanned_bytes: null } }
  };
});

write('agent-io.schema.json', agentSchema);
write('tool-receipt.schema.json', toolSchema);
write('tool-contracts.json', { status: 'Proposed; adapters not implemented', $defs: defs, tools });
for (const f of fixtures) write(`${f.task.agent_id.toLowerCase()}-example.json`, f);
const failed = structuredClone(fixtures[0].result);
failed.result_id = 'result:D1-unavailable-fixture';
failed.answer_state = 'unavailable';
failed.answer = null;
failed.errors = [{ code: 'MODEL_TIMEOUT', message: 'Model response unavailable within the reserved budget.', retryable: true, retry_after_ms: null }];
write('failed-result-example.json', failed);
const limits = { max_items: 20, timeout_ms: 5000, max_output_bytes: 16000, max_scan_bytes: 1000000 };
const currentScope = { ...scope, time_range: { start: '2026-10-20T10:45:00Z', end: '2026-10-20T10:45:01Z', basis: 'query' } };
function toolFixture(tool, args, data, evidence_refs, description, status = 'ok', error = null) {
  return { description, request: { tool, arguments: { ...args, limits } }, response: {
    call_ref: `call:fixture-${tool}`, tool, status, data, evidence_refs,
    coverage: { source_refs: tool.startsWith('code.') ? ['repo:delivery'] : ['db:messaging-replica'], actual_scope: tool.startsWith('code.') ? { ...scope, time_range: null } : currentScope,
      query_description: description, complete_for_requested_scope: status === 'ok', snapshot_refs: tool.startsWith('code.') ? ['fixture-commit-r18'] : [],
      freshness: { observed_at: '2026-10-20T10:45:00Z', watermark: null, lag_ms: null, index_updated_at: null }, sampling: null, retention: null,
      partial_reasons: status === 'ok' ? [] : [error?.message || 'Incomplete'], pages_read: status === 'ok' ? 1 : 0, scanned_bytes: null, scan_limit_reached: false },
    next_cursor: null, error, cost: { elapsed_ms: 12, backend_requests: 1, bytes_scanned: null }
  } };
}
const replica = { source_ref: 'db:messaging-replica', kind: 'replica', label: 'Messaging read replica', environment: 'production', capabilities: ['data.inspect_schema', 'data.read_bounded'], related_refs: ['db:messaging'], refreshed_at: '2026-10-20T10:45:00Z', limitations: ['Replay watermark unavailable; no configured historical row source.'] };
const readArgs = { source_ref: replica.source_ref, schema_ref: 'schema:routes-v1', read_contract_ref: 'RC1', relation: 'messaging.group_routes', columns: ['destination_id', 'legacy_destination_id'],
  filters: [{ field: 'customer_id', op: 'eq', value: 'G42' }, { field: 'active', op: 'eq', value: true }], order_by: [], query_template_ref: null, template_parameters: [], cursor: null };
const flow = [
  toolFixture('code.read_at_revision', { repository_ref: location.repository_ref, commit: location.commit, path: location.path, start_line: 40, end_line: 66 },
    { location, content: 'Synthetic excerpt: active route lookup by customer_id; read legacy_destination_id; stop on empty.' }, ['E3'], 'D4 reads only the located implementation range at a discovered immutable revision.'),
  toolFixture('data.describe_source', { source_ref: replica.source_ref }, { source: replica, primary_identity_ref: 'db:messaging', replica: true, schema_search_supported: true, history_source_refs: [], replay_watermark: null, lag_ms: null }, ['E-source'], 'D5 verifies the approved replica maps to the database identity discovered in RC1.'),
  toolFixture('data.inspect_schema', { source_ref: replica.source_ref, query: 'group_routes', relation: 'messaging.group_routes', cursor: null },
    { schema_ref: 'schema:routes-v1', relations: [{ relation: 'messaging.group_routes', kind: 'table', columns: [{ name: 'customer_id', type: 'text', nullable: false }, { name: 'active', type: 'boolean', nullable: false }, { name: 'destination_id', type: 'text', nullable: true }, { name: 'legacy_destination_id', type: 'text', nullable: true }], keys: [['customer_id']], relationships: [], evidence_refs: ['E-schema'] }] }, ['E-schema'], 'D5 verifies actual relation/column types; names came from the cited implementation, not a guess.'),
  toolFixture('data.read_bounded', readArgs, { columns: [{ name: 'destination_id', type: 'text', redacted: false }, { name: 'legacy_destination_id', type: 'text', redacted: false }], rows: [['chat-7', null]], query_ref: 'query:current-route', query_observed_at: '2026-10-20T10:45:00Z', replay_watermark: null, lag_ms: null }, ['E2'], 'D5 reads the current scoped row; this is not evidence of incident-time values at 10:32.'),
  toolFixture('data.read_bounded', readArgs, null, [], 'Alternative outcome: connector timeout is not a missing row.', 'timeout', { code: 'SOURCE_TIMEOUT', message: 'No usable result before the enforced deadline.', retryable: true, retry_after_ms: null })
];
write('tool-flow-example.json', { status: 'Synthetic teaching fixture; no real source accessed.', stages: flow });

function type(schema) {
  if (schema.$ref) return schema.$ref.split('/').at(-1);
  if (schema.const !== undefined) return JSON.stringify(schema.const);
  if (schema.enum) return schema.enum.map(x => JSON.stringify(x)).join(' / ');
  if (schema.anyOf) return schema.anyOf.map(type).join(' or ');
  if (schema.type === 'array') return `array<${type(schema.items)}>`;
  if (schema.type === 'object') return '{' + Object.entries(schema.properties || {}).map(([k, v]) => `${k}: ${type(v)}`).join(', ') + '}';
  return Array.isArray(schema.type) ? schema.type.join(' / ') : schema.type;
}
const rows = props => Object.entries(props).map(([name, schema]) => `| \`${name}\` | ${type(schema).replaceAll('|', '/')} |`).join('\n');
let catalog = `# Exact tool catalog\n\nStatus: proposed interfaces, not installed adapters. Generated from [definitions.mjs](contracts/definitions.mjs); ${tools.length} operations. Seven agent IDs; no D2. Start with [where tools execute](runtime-and-tools.md). All nested types and bounds are defined in [tool-contracts.json](contracts/tool-contracts.json).\n\n## Common calling convention\n\nThe model requests a tool name and its JSON arguments. Every input below requires every listed key, including \`limits\`; use \`null\` only where nullable, and \`[]\` for an empty list. Server caps override model limits. An empty filter cannot bypass tenant policy. Source references must come from authorized discovery; no credentials are arguments. All tool returns use the shared receipt below; operation-specific fields belong inside \`data\`.\n\n\`ToolLimits\` = {max_items: positive integer, timeout_ms: positive integer, max_output_bytes: positive integer, max_scan_bytes: nonnegative integer or null}. Null means use the connector's enforced default cap, not unlimited work.\n\n\`ToolReceipt\` = {call_ref, tool, status, data, evidence_refs, coverage, next_cursor, error, cost}. Exact schema: [tool-receipt.schema.json](contracts/tool-receipt.schema.json). The runtime records the receipt; the LLM does not manufacture it.\n\n| Status | Meaning |\n| --- | --- |\n| \`ok\` | Requested operation completed with returned data. Does not imply a diagnosis. |\n| \`empty\` | A successful search/read has no matches within recorded scope; \`data\` contains typed empty collections. Not global absence. |\n| \`partial\` | Useful data exists but pages/partitions/ranges/retention or another prerequisite are incomplete. |\n| \`denied\` | Trusted policy disallowed the operation; no permission-sensitive data leaks. |\n| \`not_found\` | A specific authorized resource/revision could not be resolved. Not an empty general search. |\n| \`unsupported\` | The configured connector lacks this operation/history/revision. |\n| \`timeout\` / \`error\` | Execution failed; error carries code/message/retryability. No automatic negative finding. |\n\nFor a hard failure with no usable result, \`data=null\`; partial results must still match that tool's data schema. Control operations may return operational status \`ok\` while their own data says pending/queued. Source evidence refs may be empty for a control operation.\n\nCoverage records actual scope, query description, source snapshots, source observation/watermark/lag/index freshness, sampling/retention, completeness, pagination and scanned bytes. Unknown values are null, not fabricated. A receipt is provenance of a query, not causal proof. See [lifecycle protocol](agent-protocol.md).\n\n## Role access profiles\n\nThe agent lists below are maximum eligible capabilities, not a permission grant. Runtime intersects role, task, authenticated tenant/source permissions and remaining budget. D7 source tools are bounded verification only. D8 cannot explore production sources; it fetches assigned originals and writes investigator-owned drafts.\n\n`;
for (const tool of tools) {
  catalog += `## ${tool.name}\n\n${tool.purpose}\n\nAgents: **${tool.agents.join(', ')}**. Executes against: ${tool.backend}.\n\nInput arguments (all keys required):\n\n| Field | Type / allowed values |\n| --- | --- |\n${rows(tool.input_schema.properties)}\n\nSuccessful/partial \`data\` object:\n\n| Field | Type / allowed values |\n| --- | --- |\n${rows(tool.data_schema.properties)}\n\nGuard/limitation: ${tool.constraints}\n\n`;
}
catalog += `## Shared types and aliases\n\nExact nested fields are in the JSON schemas. In particular: SourceLocation = repo + immutable commit + path + line range + evidence refs; EntityKey = field + scalar value + evidence refs; Scope = discovered entity/repository refs, tentative feature terms, nullable environment/time range; ReadContract = code caller + discovered connection/relation/lookup fields + version bindings + evidence + gaps.\n\nPrevious conceptual names \`code.symbol\`, \`case.read_review_snapshot\`, \`case.read_report_snapshot\` and \`ai.list_workflows/runs\` are not extra endpoints. Use \`code.search(kind="symbols")\`/\`code.references\`, \`case.read(view="review")\`, \`case.read(view="report")\` and \`ai.list_workflows\`/\`ai.list_runs\`. Generic queue/provider/cache/network/DB diagnostics in older notes map to the concrete tools above. No arbitrary shell, SQL or production mutation tool is exposed.\n`;
fs.writeFileSync(path.join(root, 'tool-catalog.md'), catalog);

const docNames = { D1: 'd1-investigation-lead', D3: 'd3-observability', D4: 'd4-code-deployment', D5: 'd5-data', D6: 'd6-ai-behavior', D7: 'd7-critic', D8: 'd8-report-writer' };
// Each role gets a small generated insert for its hand-maintained Markdown document.
// Apply these inserts to the documents with apply_patch; do not silently rewrite prose here.
for (const f of fixtures) {
  const id = f.task.agent_id;
  const permitted = tools.filter(t => t.agents.includes(id));
  const section = `## Exact runtime input, tools and structured answer\n\nRuns as a logical task in the investigation backend, not a separate VM or preloaded copy of the application. The backend executes tools and calls the model repeatedly. [Runtime and source locations](../runtime-and-tools.md).\n\nFull required Task-v1 + AgentAnswer-v1 + trusted Result-v1 fixture: [${id.toLowerCase()}-example.json](../contracts/${id.toLowerCase()}-example.json). Exact machine-readable types: [agent-io.schema.json](../contracts/agent-io.schema.json). The fixture is synthetic, not evidence or a mandatory execution order.\n\nThe task-specific \`role_input\` sent to this agent is:\n\n\`\`\`json\n${JSON.stringify(f.task.role_input, null, 2)}\n\`\`\`\n\nIt also receives the shared question, scope, known premises, unknowns, knowledge references/excerpts, dependency versions and budget. Null/empty fields mean not discovered; they are not secretly supplied. Relevant code/schema/log findings can be shared through \`knowledge\` and \`evidence.fetch\`; expertise boundaries do not isolate knowledge. Credentials and authority remain connector-side.\n\nPermitted operations (further restricted per task):\n\n| Tool | Exactly what it does |\n| --- | --- |\n${permitted.map(t => `| \`${t.name}\` | ${t.purpose} |`).join('\n')}\n\nEvery argument, returned \`data\` field, source backend and guard is specified in the [tool catalog](../tool-catalog.md). Tool errors/coverage are connector-owned receipts, distinct from the agent's interpretations.\n\nThe model returns shared fields \`agent_id\`, \`execution_status\`, \`observations\`, \`interpretations\`, \`unknowns\`, \`coverage_receipt_refs\`, \`suggested_followups\`, plus this role's required \`${extensions[id][0]}\` object:\n\n\`\`\`json\n${JSON.stringify(f.answer[extensions[id][0]], null, 2)}\n\`\`\`\n\nThis is the exact role-specific object; the linked fixture contains the whole answer and runtime wrapper. Unknowns remain explicit even on \`complete\` tasks. Runtime validates requested agent identity and source references, adds trusted task/revision IDs, actual tool errors and measured costs, then performs applicability checks before D1 uses the result. A well-formed JSON answer is not proof of semantic correctness.\n`;
  fs.writeFileSync(path.join(here, `${docNames[id]}.insert.md.txt`), section);
}
console.log(`Generated ${tools.length} tool contracts, schemas and ${fixtures.length} agent fixtures. Agent prose is not rewritten.`);
