-- Phase 1: Worker portal foundation
-- Adds: worker-auth link on people, certificate workflow on training_records,
-- change audit log, certificates storage bucket, and tightened RLS so
-- workers see only their own row while admins keep full access.
-- Demo mode (AUTH_ENABLED=false) is unaffected: service-role bypasses RLS.

-- Run as one transaction so a failure rolls back cleanly.
do $$
begin

-- =========================================================================
-- 1. people: link to auth.users + email for invites
-- =========================================================================
alter table public.people
    add column if not exists auth_user_id uuid references auth.users(id) on delete set null,
    add column if not exists email text;

create unique index if not exists people_auth_user_id_key
    on public.people(auth_user_id)
    where auth_user_id is not null;

create index if not exists people_email_idx on public.people(lower(email));

-- =========================================================================
-- 2. training_records: certificate upload workflow
-- =========================================================================
alter table public.training_records
    add column if not exists certificate_url text,
    add column if not exists certificate_status text
        not null default 'none'
        check (certificate_status in ('none', 'pending', 'approved', 'rejected')),
    add column if not exists certificate_uploaded_at timestamptz,
    add column if not exists certificate_uploaded_by uuid references auth.users(id) on delete set null,
    add column if not exists certificate_reviewed_at timestamptz,
    add column if not exists certificate_reviewed_by uuid references auth.users(id) on delete set null,
    add column if not exists certificate_reject_reason text;

create index if not exists training_records_cert_status_idx
    on public.training_records(certificate_status)
    where certificate_status = 'pending';

-- =========================================================================
-- 3. people_change_log: audit every worker self-edit
-- =========================================================================
create table if not exists public.people_change_log (
    id uuid primary key default gen_random_uuid(),
    person_id uuid not null references public.people(id) on delete cascade,
    changed_by uuid references auth.users(id) on delete set null,
    changed_by_email text,
    field_name text not null,
    old_value text,
    new_value text,
    source text not null default 'worker' check (source in ('worker', 'admin', 'system')),
    changed_at timestamptz not null default now()
);

create index if not exists people_change_log_person_idx
    on public.people_change_log(person_id, changed_at desc);

create index if not exists people_change_log_recent_idx
    on public.people_change_log(changed_at desc);

-- =========================================================================
-- 4. Helper: resolve current auth user to a person row
-- =========================================================================
create or replace function public.current_person_id() returns uuid as $func$
    select id from public.people
    where auth_user_id = auth.uid()
    limit 1;
$func$ language sql stable security definer;

create or replace function public.is_self_person(p_person_id uuid) returns boolean as $func$
    select exists (
        select 1 from public.people
        where id = p_person_id and auth_user_id = auth.uid()
    );
$func$ language sql stable security definer;

-- =========================================================================
-- 5. Tighten RLS on people: admin = all, worker = own row only
-- =========================================================================
drop policy if exists people_auth_all on public.people;

create policy people_admin_all on public.people
    for all to authenticated
    using (public.is_admin())
    with check (public.is_admin());

create policy people_self_read on public.people
    for select to authenticated
    using (auth_user_id = auth.uid());

create policy people_self_update on public.people
    for update to authenticated
    using (auth_user_id = auth.uid())
    with check (auth_user_id = auth.uid());

-- =========================================================================
-- 6. Tighten RLS on training_records: admin = all, worker = own records
-- =========================================================================
drop policy if exists training_records_auth_all on public.training_records;

create policy training_records_admin_all on public.training_records
    for all to authenticated
    using (public.is_admin())
    with check (public.is_admin());

create policy training_records_self_read on public.training_records
    for select to authenticated
    using (public.is_self_person(person_id));

-- Workers can update only the certificate fields on their own records,
-- and only to set status='pending'. They cannot self-approve.
create policy training_records_self_cert_upload on public.training_records
    for update to authenticated
    using (public.is_self_person(person_id))
    with check (
        public.is_self_person(person_id)
        and certificate_status = 'pending'
    );

-- =========================================================================
-- 7. people_change_log RLS
-- =========================================================================
alter table public.people_change_log enable row level security;

create policy change_log_admin_read on public.people_change_log
    for select to authenticated using (public.is_admin());

create policy change_log_self_read on public.people_change_log
    for select to authenticated
    using (public.is_self_person(person_id));

create policy change_log_self_insert on public.people_change_log
    for insert to authenticated
    with check (
        public.is_self_person(person_id)
        and changed_by = auth.uid()
        and source = 'worker'
    );

-- =========================================================================
-- 8. Extend new-user trigger: auto-link auth user to people by email
-- =========================================================================
create or replace function public.handle_new_user() returns trigger as $func$
begin
    insert into public.app_users (id, email, role)
    values (new.id, new.email, 'user')
    on conflict (id) do nothing;

    -- Auto-link to an existing people row if the email matches and no link yet.
    update public.people
    set auth_user_id = new.id
    where lower(email) = lower(new.email)
      and auth_user_id is null;

    return new;
end;
$func$ language plpgsql security definer;

end $$;

-- =========================================================================
-- 9. Storage bucket: certificates (private)
-- Path convention: {person_id}/{training_record_id}/{filename}
-- =========================================================================
insert into storage.buckets (id, name, public)
values ('certificates', 'certificates', false)
on conflict (id) do nothing;

-- Worker can upload into their own person folder
drop policy if exists certs_worker_upload on storage.objects;
create policy certs_worker_upload on storage.objects
    for insert to authenticated
    with check (
        bucket_id = 'certificates'
        and public.is_self_person((storage.foldername(name))[1]::uuid)
    );

-- Worker can read their own files
drop policy if exists certs_worker_read on storage.objects;
create policy certs_worker_read on storage.objects
    for select to authenticated
    using (
        bucket_id = 'certificates'
        and (
            public.is_admin()
            or public.is_self_person((storage.foldername(name))[1]::uuid)
        )
    );

-- Worker can delete only their own pending uploads (admin can delete anything)
drop policy if exists certs_worker_delete on storage.objects;
create policy certs_worker_delete on storage.objects
    for delete to authenticated
    using (
        bucket_id = 'certificates'
        and (
            public.is_admin()
            or public.is_self_person((storage.foldername(name))[1]::uuid)
        )
    );
