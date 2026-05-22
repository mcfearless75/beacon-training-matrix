-- People
create table public.people (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    job_title text,
    paye boolean,
    ni_number text,
    start_date date,
    active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Training types
create table public.training_types (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    code text,
    notes text,
    active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Training records (one current row per person+type)
create table public.training_records (
    id uuid primary key default gen_random_uuid(),
    person_id uuid not null references public.people(id) on delete cascade,
    training_type_id uuid not null references public.training_types(id) on delete restrict,
    completed_date date,
    expiry_date date,
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (person_id, training_type_id)
);

create index training_records_expiry_idx on public.training_records (expiry_date) where expiry_date is not null;

-- Reminder log (dedupe + audit). "window" is quoted because it is a reserved keyword in Postgres.
create table public.reminder_log (
    id uuid primary key default gen_random_uuid(),
    training_record_id uuid not null references public.training_records(id) on delete cascade,
    "window" text not null check ("window" in ('90','30','7','expired')),
    sent_at timestamptz not null default now(),
    recipient_email text not null,
    status text not null check (status in ('sent','failed')),
    error text,
    unique (training_record_id, "window")
);

-- Settings (single-row)
create table public.settings (
    id int primary key default 1,
    reminder_recipient_email text,
    sender_name text default 'Beacon Training Matrix',
    sender_email text,
    updated_at timestamptz not null default now(),
    constraint settings_singleton check (id = 1)
);

-- App users (role mapping)
create table public.app_users (
    id uuid primary key references auth.users(id) on delete cascade,
    email text not null,
    role text not null check (role in ('admin','user')) default 'user',
    created_at timestamptz not null default now()
);

-- updated_at trigger
create or replace function public.set_updated_at() returns trigger as $$
begin new.updated_at = now(); return new; end;
$$ language plpgsql;

create trigger trg_people_updated before update on public.people
    for each row execute function public.set_updated_at();
create trigger trg_training_types_updated before update on public.training_types
    for each row execute function public.set_updated_at();
create trigger trg_training_records_updated before update on public.training_records
    for each row execute function public.set_updated_at();
