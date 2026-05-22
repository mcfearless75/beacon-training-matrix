insert into public.settings (id, reminder_recipient_email, sender_name, sender_email)
values (1, null, 'Beacon Training Matrix', null)
on conflict (id) do nothing;
