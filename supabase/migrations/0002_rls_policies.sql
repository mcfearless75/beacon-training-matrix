-- Helper: is current user an admin?
create or replace function public.is_admin() returns boolean as $$
    select exists (
        select 1 from public.app_users
        where id = auth.uid() and role = 'admin'
    );
$$ language sql stable security definer;

-- Enable RLS
alter table public.people enable row level security;
alter table public.training_types enable row level security;
alter table public.training_records enable row level security;
alter table public.reminder_log enable row level security;
alter table public.settings enable row level security;
alter table public.app_users enable row level security;

-- people: any authenticated user reads + writes
create policy people_auth_all on public.people
    for all to authenticated using (true) with check (true);

-- training_types: read for all auth; write for admin only
create policy training_types_read on public.training_types
    for select to authenticated using (true);
create policy training_types_admin_write on public.training_types
    for insert to authenticated with check (public.is_admin());
create policy training_types_admin_update on public.training_types
    for update to authenticated using (public.is_admin());
create policy training_types_admin_delete on public.training_types
    for delete to authenticated using (public.is_admin());

-- training_records: any auth user
create policy training_records_auth_all on public.training_records
    for all to authenticated using (true) with check (true);

-- reminder_log: admin reads only; cron writes via service role (bypasses RLS)
create policy reminder_log_admin_read on public.reminder_log
    for select to authenticated using (public.is_admin());

-- settings: read any auth; write admin only
create policy settings_read on public.settings
    for select to authenticated using (true);
create policy settings_admin_update on public.settings
    for update to authenticated using (public.is_admin());

-- app_users: read own row; admin reads + writes all
create policy app_users_read_own on public.app_users
    for select to authenticated using (id = auth.uid() or public.is_admin());
create policy app_users_admin_write on public.app_users
    for insert to authenticated with check (public.is_admin());
create policy app_users_admin_update on public.app_users
    for update to authenticated using (public.is_admin());
