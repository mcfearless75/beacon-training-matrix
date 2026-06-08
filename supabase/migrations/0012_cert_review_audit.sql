-- Phase 3: Certificate review audit
-- Adds: certificate_review_log table + trigger that auto-records every
-- approve/reject decision on training_records. Separate from people_change_log
-- (which is for worker self-edits) so the Approvals queue has a clean audit
-- trail keyed on the training_record itself.

do $$
begin

create table if not exists public.certificate_review_log (
    id uuid primary key default gen_random_uuid(),
    training_record_id uuid not null references public.training_records(id) on delete cascade,
    person_id uuid not null references public.people(id) on delete cascade,
    action text not null check (action in ('approved', 'rejected')),
    reviewed_by uuid references auth.users(id) on delete set null,
    reviewed_by_email text,
    reject_reason text,
    certificate_url text,
    reviewed_at timestamptz not null default now()
);

create index if not exists cert_review_log_record_idx
    on public.certificate_review_log(training_record_id, reviewed_at desc);

create index if not exists cert_review_log_person_idx
    on public.certificate_review_log(person_id, reviewed_at desc);

create index if not exists cert_review_log_recent_idx
    on public.certificate_review_log(reviewed_at desc);

alter table public.certificate_review_log enable row level security;

create policy cert_review_log_admin_read on public.certificate_review_log
    for select to authenticated using (public.is_admin());

create policy cert_review_log_admin_insert on public.certificate_review_log
    for insert to authenticated with check (public.is_admin());

create policy cert_review_log_self_read on public.certificate_review_log
    for select to authenticated
    using (public.is_self_person(person_id));

end $$;

-- Trigger: when certificate_status flips to approved or rejected, write a log row.
create or replace function public.log_certificate_review() returns trigger as $func$
declare
    reviewer_email text;
begin
    if new.certificate_status in ('approved', 'rejected')
       and (old.certificate_status is distinct from new.certificate_status) then
        select email into reviewer_email
        from auth.users
        where id = new.certificate_reviewed_by;

        insert into public.certificate_review_log (
            training_record_id, person_id, action,
            reviewed_by, reviewed_by_email,
            reject_reason, certificate_url
        ) values (
            new.id, new.person_id, new.certificate_status,
            new.certificate_reviewed_by, reviewer_email,
            new.certificate_reject_reason, new.certificate_url
        );
    end if;
    return new;
end;
$func$ language plpgsql security definer;

drop trigger if exists training_records_cert_review_log on public.training_records;
create trigger training_records_cert_review_log
    after update of certificate_status on public.training_records
    for each row execute function public.log_certificate_review();
