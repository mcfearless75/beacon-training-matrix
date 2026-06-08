# Client Login Runbook

How to switch Beacon Training Matrix from demo mode to real worker logins.
Follow top to bottom. Each step is independent unless noted.

---

## 1. Railway — enable auth

1. Open the Beacon project on Railway → **Variables**.
2. Add / confirm these:
   - `AUTH_ENABLED=true`
   - `SUPABASE_URL` — your project URL
   - `SUPABASE_ANON_KEY` — anon/publishable key
   - `SUPABASE_SERVICE_ROLE_KEY` — service-role key (needed for the Invite button)
3. Railway will redeploy automatically. Wait for the deploy to go green.

**Sanity check:** open the deployed URL — you should now see the OTP login screen, not the welcome page.

---

## 2. First-admin bootstrap (one-time)

The `handle_new_user` trigger creates every new sign-in as `role='user'`. Sign in once first so your row exists, then promote yourself.

1. Sign in at the deployed URL with `paulmc18@gmail.com` via OTP.
2. You'll land on **My Profile** as a normal worker (that's expected — you're still `role='user'`).
3. Open Supabase → **SQL Editor** → run:
   ```sql
   update public.app_users
   set role = 'admin'
   where email = 'paulmc18@gmail.com';
   ```
4. Click **Sign out** in the sidebar → sign back in → you should now see the full admin sidebar (Workforce / Reviews / Drill-down / Setup).

---

## 3. Supabase — invite-only auth

Workers should only get in via the Invite button on the People page. Lock down public signup.

1. Supabase → **Authentication → Providers → Email**:
   - **Enable Email provider:** on
   - **Confirm email:** on
   - **Allow new users to sign up:** **off** (invite-only)
   - **Secure email change:** on
2. Supabase → **Authentication → URL Configuration**:
   - **Site URL:** your Railway URL (no trailing slash)
   - **Redirect URLs:** add the Railway URL + `http://localhost:8501` (for local dev)
3. Supabase → **Authentication → Email Templates → Invite User**:
   - Subject: `You've been invited to Beacon Training Matrix`
   - Body: replace default with Beacon-branded copy. Keep `{{ .ConfirmationURL }}` and `{{ .Token }}` placeholders intact.

---

## 4. SMTP — escape Supabase's rate limit

Supabase's default email sender is rate-limited (~4/hour). Fine for testing, breaks the moment you invite multiple workers.

**Cheapest path:** SendGrid free tier (100/day).

1. Sign up at sendgrid.com → verify a sender identity (`hello@beaconrisk.co.uk` or similar).
2. Create an API key with **Mail Send → Full Access**.
3. Supabase → **Project Settings → Auth → SMTP Settings**:
   - **Enable Custom SMTP:** on
   - **Host:** `smtp.sendgrid.net`
   - **Port:** `587`
   - **Username:** `apikey` (literal word)
   - **Password:** your SendGrid API key
   - **Sender email / name:** your verified sender + "Beacon Training Matrix"
4. Save → send a test invite to your own non-Beacon email.

**Upgrade path** when volume grows: Postmark or Resend, ~£10–15/mo, better deliverability than SendGrid free.

---

## 5. End-to-end test

1. As admin, open **People** → add a new person with a real email you can receive at → click **Invite to portal**.
2. Within ~30s, that email should receive a Beacon-branded invite with a magic link.
3. Click the link → land on the OTP page → request and enter code → sign in.
4. Confirm:
   - Sidebar shows **My Profile** only.
   - The `invites` row for that email has `accepted_at` populated (check in Supabase Table Editor).
   - The `people` row for that worker has `auth_user_id` populated (auto-linked by the trigger).
5. As the worker, upload a test certificate against a training row → confirm `certificate_status = 'pending'`.
6. Sign out → sign back in as admin → open **Approvals** → approve the cert → confirm a row lands in `certificate_review_log`.

---

## Known gaps (handle when they bite)

- **Worker changes their email on My Profile** → `auth_user_id` doesn't relink. Workaround: lock the email field for workers, or add a server-side trigger to relink on email change.
- **Worker is deactivated** → setting `people.active=false` doesn't revoke their auth session. They can still sign in until their JWT expires. Add a Supabase Auth admin call to `delete_user` from the People page if you need hard revocation.
- **OTP rate limit lockout** → if a worker requests too many codes, Supabase blocks them for ~30 minutes. Document this for clients before they raise it as a bug.

---

## Rollback

If something breaks and you need to drop back to demo mode:
1. Railway → set `AUTH_ENABLED=false` → redeploy.
2. The app reverts to single-tenant admin-as-everyone. Worker accounts still exist in Supabase but the login screen is bypassed.
