create or replace function public.get_active_training_records()
returns table (
    id uuid,
    expiry_date date,
    person_name text,
    training_name text
) language sql security definer as $$
    select tr.id, tr.expiry_date, p.name as person_name, tt.name as training_name
    from public.training_records tr
    join public.people p on p.id = tr.person_id and p.active
    join public.training_types tt on tt.id = tr.training_type_id and tt.active
    where tr.expiry_date is not null;
$$;
grant execute on function public.get_active_training_records() to service_role;
grant execute on function public.get_active_training_records() to authenticated;
