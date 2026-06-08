-- Phase 3: Worker invites
-- Tracks who was invited, when, by whom, and whether they've accepted.
-- The actual auth.users row is created via supabase.auth.admin.create_user()
-- from the People page (see CLAUDE.md: never insert into auth.users via SQL).
-- This table records the invite intent + audit trail.

do $$
begin

create table if not exists public.invites (
    id uuid primary key default gen_random_uuid(),
    email text not null,
    person_id uuid references public.people(id) on delete set null,
    invited_by uuid references auth.users(id) on delete set null,
    invited_by_email text,
    invited_at timestamptz not null default now(),
    accepted_at timestamptz,
    accepted_auth_user_id uuid references auth.users(id) on delete set null,
    revoked_at timestamptz,
    note text
);

create unique index if not exists invites_email_pending_key
    on public.invites(lower(email))
    where accepted_at is null and revoked_at is null;

create index if not exists invites_person_idx on public.invites(person_id);
create index if not exists invites_pending_idx
    on public.invites(invited_at desc)
    where accepted_at is null and revoked_at is null;

alter table public.invites enable row level security;

create policy invites_admin_all on public.invites
    for all to authenticated
    using (public.is_admin())
    with check (public.is_admin());

end $$;

-- Extend the new-user trigger: when an invited email signs in for the first
-- time, mark the matching invite as accepted.
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

    -- Mark any pending invite for this email as accepted.
    update public.invites
    set accepted_at = now(),
        accepted_auth_user_id = new.id
    where lower(email) = lower(new.email)
      and accepted_at is null
      and revoked_at is null;

    return new;
end;
$func$ language plpgsql security definer;
