create table if not exists workflow_runs (
  id uuid primary key default gen_random_uuid(),
  goal text not null,
  status text not null,
  final_output jsonb,
  created_at timestamp default now()
);

create table if not exists agent_runs (
  id uuid primary key default gen_random_uuid(),
  workflow_id uuid references workflow_runs(id) on delete cascade,
  agent_name text not null,
  input jsonb,
  output jsonb,
  created_at timestamp default now()
);
