-- Dedicated demo schema. This is intentionally separate from application tables.
-- Run with the Supabase CLI or scripts/migrate.py against an approved demo project.

create schema if not exists incident;

create table if not exists incident.cases (
  case_id text primary key,
  complaint text not null check (char_length(complaint) between 8 and 2000),
  scenario_id text not null,
  tenant_id text not null,
  requested_by text not null,
  status text not null check (status in ('open', 'investigating', 'reviewing', 'delivered', 'withheld', 'failed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists incident.agent_runs (
  run_id text primary key,
  case_id text not null references incident.cases(case_id) on delete cascade,
  task_id text not null,
  role text not null check (role in ('D1', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8')),
  operation text not null,
  model_name text not null,
  langsmith_run_name text not null,
  status text not null check (status in ('started', 'succeeded', 'failed')),
  error_message text,
  input_json jsonb not null default '{}'::jsonb,
  output_json jsonb,
  started_at timestamptz not null default now(),
  completed_at timestamptz
);
create index if not exists agent_runs_case_idx on incident.agent_runs(case_id, started_at);

create table if not exists incident.tool_calls (
  tool_call_id text primary key,
  case_id text not null references incident.cases(case_id) on delete cascade,
  task_id text not null,
  run_id text not null references incident.agent_runs(run_id) on delete cascade,
  role text not null check (role in ('D3', 'D4', 'D5', 'D6')),
  tool_name text not null,
  arguments_json jsonb not null,
  status text not null check (status in ('succeeded', 'rejected', 'failed')),
  result_count integer not null default 0 check (result_count >= 0),
  created_at timestamptz not null default now()
);
create index if not exists tool_calls_case_idx on incident.tool_calls(case_id, created_at);

create table if not exists incident.evidence (
  evidence_id text primary key,
  case_id text not null references incident.cases(case_id) on delete cascade,
  tool_call_id text not null references incident.tool_calls(tool_call_id) on delete cascade,
  source_kind text not null check (source_kind in ('observability', 'code_deploy', 'data', 'ai_runtime')),
  source_record_id text not null,
  observed_at timestamptz not null,
  summary text not null,
  coverage_note text not null,
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists evidence_case_idx on incident.evidence(case_id, created_at);

create table if not exists incident.findings (
  finding_id text primary key,
  case_id text not null references incident.cases(case_id) on delete cascade,
  task_id text not null,
  role text not null check (role in ('D3', 'D4', 'D5', 'D6')),
  finding_json jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists findings_case_idx on incident.findings(case_id, created_at);

create table if not exists incident.report_revisions (
  report_id text primary key,
  case_id text not null references incident.cases(case_id) on delete cascade,
  report_json jsonb not null,
  d7_approved boolean not null,
  created_at timestamptz not null default now()
);

-- These records emulate separate external read sources for the demo. They are never injected
-- wholesale into a prompt; each agent accesses them only through a bounded gateway tool.
create table if not exists incident.demo_scenarios (
  scenario_id text primary key,
  title text not null,
  description text not null
);

create table if not exists incident.demo_source_records (
  source_record_id text primary key,
  scenario_id text not null references incident.demo_scenarios(scenario_id) on delete cascade,
  source_kind text not null check (source_kind in ('observability', 'code_deploy', 'data', 'ai_runtime')),
  observed_at timestamptz not null,
  summary text not null,
  content text not null,
  coverage_note text not null,
  metadata jsonb not null default '{}'::jsonb
);
create index if not exists demo_source_scope_idx on incident.demo_source_records(scenario_id, source_kind, observed_at desc);

-- A database role used for the demo should receive only CONNECT/USAGE/SELECT on incident.
-- Do not reuse a Supabase application service-role or give the OpenAI process database credentials.
