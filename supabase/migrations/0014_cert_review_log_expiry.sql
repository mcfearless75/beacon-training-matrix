-- Phase 4: capture the record's expiry_date at the moment of either decision
-- (approved or rejected). Closes a gap where approving a certificate never
-- recorded (or updated) the expiry date it was approved with, leaving the
-- audit trail silent on the one field the reminder cron depends on.

alter table public.certificate_review_log
    add column if not exists expiry_date date;

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
            reject_reason, certificate_url, expiry_date
        ) values (
            new.id, new.person_id, new.certificate_status,
            new.certificate_reviewed_by, reviewer_email,
            new.certificate_reject_reason, new.certificate_url, new.expiry_date
        );
    end if;
    return new;
end;
$func$ language plpgsql security definer;
