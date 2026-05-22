create or replace function public.handle_new_user() returns trigger as $$
begin
    insert into public.app_users (id, email, role)
    values (new.id, new.email, 'user')
    on conflict (id) do nothing;
    return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();
