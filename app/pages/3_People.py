from datetime import date

import streamlit as st

from app.auth import current_user_email, require_admin
from app.branding import help_box, inject_css, page_header
from beacon.db import anon_client, service_client
from beacon.reminders import compliance_summary

require_admin()
inject_css()
page_header("People", "Add, edit, and manage workforce records.")
help_box(
    "Managing people",
    "Add new starters with the form below. Click any name to expand and edit their details. "
    "Set someone to <b>inactive</b> to remove them from the Matrix — their training history is preserved.",
)

sb = service_client()  # admin page — service role bypasses RLS; page is gated by require_admin()

# ===== Add new person =====
with st.expander("Add new person", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        new_name = st.text_input("Full name *", key="new_name")
        new_job = st.text_input("Job title", key="new_job")
        new_paye = st.checkbox("PAYE employee", key="new_paye")
    with c2:
        new_email = st.text_input("Work email", key="new_email", help="Required if you want to invite them to the portal later.")
        new_ni = st.text_input("NI number", key="new_ni")
        new_start = st.date_input("Start date", value=None, key="new_start")
    if st.button("Add person", key="add_person", type="primary"):
        if not new_name.strip():
            st.error("Name is required.")
        else:
            try:
                sb.table("people").insert({
                    "name": new_name.strip(),
                    "job_title": new_job.strip() or None,
                    "paye": new_paye,
                    "ni_number": new_ni.strip() or None,
                    "email": new_email.strip().lower() or None,
                    "start_date": new_start.isoformat() if new_start else None,
                }).execute()
                st.success(f"Added {new_name.strip()}.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not add person — {e}")

# ===== Load data =====
people = sb.table("people").select("*").order("name").execute().data

# Compute compliance per person in a single query
today = date.today()
all_records_raw = (
    sb.table("training_records")
    .select("person_id, expiry_date")
    .execute()
    .data
)
records_by_person: dict[str, list] = {}
rec_count_by_person: dict[str, int] = {}
for r in all_records_raw:
    pid = r["person_id"]
    records_by_person.setdefault(pid, []).append(
        {"expiry_date": date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None}
    )
    rec_count_by_person[pid] = rec_count_by_person.get(pid, 0) + 1


def _person_compliance(pid: str) -> dict | None:
    recs = records_by_person.get(pid)
    if not recs:
        return None
    return compliance_summary(recs, today=today)


def _badge_tone(s: dict | None) -> str:
    if s is None:
        return "grey"
    if s["expired"] > 0 or s["score"] < 50:
        return "red"
    if s["score"] < 85:
        return "amber"
    return "green"


def _badge_text(s: dict | None) -> str:
    if s is None:
        return "No records"
    issues = s["expired"] + s["week"]
    if issues == 0:
        return f"{s['score']}% compliant"
    noun = "issue" if issues == 1 else "issues"
    return f"{issues} {noun}"


# ===== Search + stats =====
search = st.text_input(
    "Search people",
    placeholder="Search by name or job title…",
    label_visibility="collapsed",
).strip().lower()

all_active = [p for p in people if p.get("active")]
all_inactive = [p for p in people if not p.get("active")]
st.caption(
    f"**{len(all_active)} active** · {len(all_inactive)} inactive · {len(people)} total"
)

# Apply search filter
def _matches(p):
    return search in f"{p['name']} {p.get('job_title') or ''}".lower()

active_list = [p for p in all_active if not search or _matches(p)]
inactive_list = [p for p in all_inactive if not search or _matches(p)]

# ===== Tabs =====
tab_active, tab_inactive = st.tabs([
    f"Active  ({len(active_list)})",
    f"Inactive  ({len(inactive_list)})",
])


def _render_people(plist: list, tab_key: str) -> None:
    if not plist:
        st.info("No people found." if search else "None here yet.")
        return

    for p in plist:
        s = _person_compliance(p["id"])
        tone = _badge_tone(s)
        badge_text = _badge_text(s)
        rec_count = rec_count_by_person.get(p["id"], 0)
        rec_label = f"{rec_count} record{'s' if rec_count != 1 else ''}"

        expander_label = f"{p['name']}  ·  {badge_text}  ·  {rec_label}"
        if not p.get("active"):
            expander_label += "  (inactive)"

        with st.expander(expander_label):
            # Compliance badge + last login
            last_login = p.get("last_login")
            if last_login:
                try:
                    from datetime import datetime, timezone
                    ll = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
                    ll_fmt = ll.strftime("%d %b %Y, %H:%M")
                except Exception:
                    ll_fmt = last_login
            else:
                ll_fmt = "Never signed in"
            st.markdown(
                f'<div style="margin-bottom:14px;">'
                f'<span class="compliance-badge {tone}">{badge_text}</span>'
                f'&nbsp;&nbsp;<span style="color:#64748B;font-size:0.82rem;">Last login: {ll_fmt}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                new_title = st.text_input(
                    "Job title",
                    value=p.get("job_title") or "",
                    key=f"jt_{tab_key}_{p['id']}",
                )
                new_ni = st.text_input(
                    "NI number",
                    value=p.get("ni_number") or "",
                    key=f"ni_{tab_key}_{p['id']}",
                    help="National Insurance number — stored for reference only.",
                )
                new_email = st.text_input(
                    "Work email",
                    value=p.get("email") or "",
                    key=f"em_{tab_key}_{p['id']}",
                    help="Used to invite them to the worker portal.",
                )
            with col2:
                new_paye = st.checkbox(
                    "PAYE employee",
                    value=bool(p.get("paye")),
                    key=f"paye_{tab_key}_{p['id']}",
                )
                new_start = st.date_input(
                    "Start date",
                    value=date.fromisoformat(p["start_date"]) if p.get("start_date") else None,
                    key=f"sd_{tab_key}_{p['id']}",
                )
                new_active = st.checkbox(
                    "Active",
                    value=bool(p.get("active")),
                    key=f"act_{tab_key}_{p['id']}",
                )

            btn_col, invite_col, link_col = st.columns([1, 1, 1])
            with btn_col:
                if st.button("Save changes", key=f"sv_{tab_key}_{p['id']}", type="primary"):
                    new_email_clean = new_email.strip().lower() or None
                    old_email_clean = (p.get("email") or "").lower() or None
                    email_changed = new_email_clean != old_email_clean
                    payload = {
                        "job_title": new_title.strip() or None,
                        "ni_number": new_ni.strip() or None,
                        "email": new_email_clean,
                        "paye": new_paye,
                        "start_date": new_start.isoformat() if new_start else None,
                        "active": new_active,
                    }
                    # Email changed — clear the auth link so it re-links by email
                    # on the worker's next sign-in (avoids stale auth_user_id mapping).
                    if email_changed:
                        payload["auth_user_id"] = None
                    sb.table("people").update(payload).eq("id", p["id"]).execute()
                    if email_changed:
                        st.success("Saved. Auth link cleared — worker must sign in again to re-link.")
                    else:
                        st.success("Saved.")
                    st.rerun()
            with invite_col:
                already_linked = bool(p.get("auth_user_id"))
                invite_target = (new_email.strip().lower() or (p.get("email") or "").lower())
                invite_disabled = already_linked or not invite_target
                invite_label = "Already linked" if already_linked else "Invite to portal"
                if st.button(
                    invite_label,
                    key=f"inv_{tab_key}_{p['id']}",
                    disabled=invite_disabled,
                    use_container_width=True,
                ):
                    try:
                        admin_sb = service_client()
                        # Send the Supabase invite email (magic link).
                        # auth.admin.invite_user_by_email is the ONLY supported path —
                        # never insert directly into auth.users (see CLAUDE.md).
                        already_existed = False
                        try:
                            try:
                                admin_sb.auth.admin.invite_user_by_email(
                                    invite_target,
                                    {"data": {"person_id": str(p["id"])}},
                                )
                            except TypeError:
                                # Older supabase-py signature without options kwarg.
                                admin_sb.auth.admin.invite_user_by_email(invite_target)
                        except Exception as invite_err:
                            # If the user already exists, Supabase re-sends the invite
                            # but may also raise — treat duplicates as benign.
                            msg = str(invite_err).lower()
                            if "already" in msg or "registered" in msg or "exists" in msg:
                                already_existed = True
                            else:
                                raise

                        # Persist email on people row if it changed.
                        if (p.get("email") or "").lower() != invite_target:
                            sb.table("people").update({"email": invite_target}).eq("id", p["id"]).execute()

                        # Record the invite (unique partial index prevents duplicate pending).
                        invited_by_email = current_user_email()
                        try:
                            sb.table("invites").insert({
                                "email": invite_target,
                                "person_id": p["id"],
                                "invited_by_email": invited_by_email,
                            }).execute()
                        except Exception as insert_err:
                            # Duplicate pending invite — update the existing row instead.
                            msg = str(insert_err).lower()
                            if "duplicate" in msg or "unique" in msg or "23505" in msg:
                                from datetime import datetime, timezone
                                # invites has no 'status' column — pending = accepted_at null & revoked_at null
                                sb.table("invites").update({
                                    "invited_at": datetime.now(timezone.utc).isoformat(),
                                    "invited_by_email": invited_by_email,
                                }).eq("email", invite_target).is_("accepted_at", "null").is_("revoked_at", "null").execute()
                            else:
                                raise

                        if already_existed:
                            st.success(f"User already exists — invite link re-sent to {invite_target}.")
                        else:
                            st.success(f"Invite email sent to {invite_target}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not invite — {e}")
            with link_col:
                try:
                    st.page_link("pages/7_Profile.py", label="View full profile →")
                except Exception:
                    st.caption("See Profile page for full detail.")


with tab_active:
    _render_people(active_list, "act")

with tab_inactive:
    _render_people(inactive_list, "inact")
