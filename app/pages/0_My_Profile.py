"""Worker self-service portal.

Lets a signed-in worker view their compliance, edit their own contact
details (every change written to people_change_log), and upload
certificates for individual training records (queued as pending until
an admin approves).

Demo mode (AUTH_ENABLED=false): no real auth, so the page presents a
person picker that simulates "logged in as <name>".
"""

from datetime import date, datetime, timezone

import streamlit as st

from app.auth import (
    _auth_enabled,
    current_person,
    current_user_email,
    get_session,
    require_worker_or_admin,
)
from app.branding import help_box, inject_css, page_header
from beacon.db import anon_client, service_client
from beacon.reminders import classify_window, compliance_summary

require_worker_or_admin()
inject_css()
page_header(
    "My Profile",
    "Keep your details up to date and upload certificates as you renew them.",
)


def _client():
    """Return a Supabase client bound to the worker's session when AUTH_ENABLED,
    otherwise service-role (demo mode has no auth.uid())."""
    sb = anon_client()
    if _auth_enabled():
        session = get_session()
        if session:
            sb.auth.set_session(session.access_token, session.refresh_token)
    return sb


def _current_auth_uid() -> str | None:
    if not _auth_enabled():
        return None
    session = get_session()
    return getattr(getattr(session, "user", None), "id", None) if session else None


sb = _client()
sb_admin = service_client()  # used only for demo-mode picker reads + change-log inserts


# --------------------------------------------------------------------------
# Resolve "who is this"
# --------------------------------------------------------------------------
def _demo_picker() -> dict | None:
    people = (
        sb_admin.table("people")
        .select("id, name, job_title, email, phone, address, start_date, paye, active")
        .eq("active", True)
        .order("name")
        .execute()
        .data
        or []
    )
    if not people:
        st.info("Add a person on the People page first.")
        return None
    st.warning("Demo mode — AUTH_ENABLED is off. Pick a worker to simulate.")
    picked = st.selectbox(
        "Simulate as",
        options=people,
        format_func=lambda p: f"{p['name']} — {p.get('job_title') or '—'}",
    )
    st.session_state["demo_person"] = picked
    return picked


person = current_person()
if person is None and not _auth_enabled():
    person = _demo_picker()

if person is None:
    email = current_user_email() or "your email"
    st.error(
        f"No profile is linked to **{email}** yet. "
        "Please ask your admin to invite you from the People page."
    )
    st.stop()


# --------------------------------------------------------------------------
# Identity card + compliance
# --------------------------------------------------------------------------
records_raw = (
    sb.table("training_records")
    .select(
        "id, training_type_id, completed_date, expiry_date, notes, "
        "certificate_url, certificate_status, certificate_uploaded_at, "
        "certificate_reject_reason"
    )
    .eq("person_id", person["id"])
    .execute()
    .data
    or []
)
types = {
    t["id"]: t["name"]
    for t in sb.table("training_types").select("id, name").execute().data
}

today = date.today()
records_for_calc = [
    {"expiry_date": date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None}
    for r in records_raw
]
summary = compliance_summary(records_for_calc, today=today)

score_colour = (
    "#16A34A" if summary["score"] >= 75
    else "#D97706" if summary["score"] >= 50
    else "#DC2626"
)
ident_html = (
    '<div class="profile-card">'
    f'<div class="profile-avatar">{(person["name"][:1] or "?").upper()}</div>'
    '<div class="profile-meta">'
    f'<div class="profile-name">{person["name"]}</div>'
    f'<div class="profile-job">{person.get("job_title") or "—"}</div>'
    f'<div class="profile-start">Joined: {person.get("start_date") or "—"}</div>'
    '</div></div>'
    '<div class="profile-stats">'
    f'<div class="profile-stat"><div class="ps-value" style="color:{score_colour};">'
    f'{summary["score"]}%</div><div class="ps-label">Compliance</div></div>'
    f'<div class="profile-stat"><div class="ps-value" style="color:#DC2626;">'
    f'{summary["expired"]}</div><div class="ps-label">Expired</div></div>'
    f'<div class="profile-stat"><div class="ps-value" style="color:#D97706;">'
    f'{summary["week"] + summary["month"]}</div><div class="ps-label">Due ≤30 days</div></div>'
    f'<div class="profile-stat"><div class="ps-value">{len(records_raw)}</div>'
    '<div class="ps-label">Records</div></div>'
    '</div>'
)
st.markdown(ident_html, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Editable details (every change is logged)
# --------------------------------------------------------------------------
EDITABLE_FIELDS = [
    ("name", "Full name", "text"),
    ("email", "Email", "text"),
    ("phone", "Phone", "text"),
    ("address", "Address", "textarea"),
    ("ni_number", "NI number", "text"),
    ("next_of_kin_name", "Next of kin — name", "text"),
    ("next_of_kin_phone", "Next of kin — phone", "text"),
]


with st.expander("My details", expanded=False):
    st.caption("Changes are saved immediately and logged for your admin.")
    with st.form("profile_edit"):
        new_values: dict[str, str | None] = {}
        for key, label, kind in EDITABLE_FIELDS:
            current = person.get(key) or ""
            # Workers must not change their sign-in email — it's their auth credential.
            # Show it read-only in live auth mode; demo mode leaves it editable for admin testing.
            if key == "email" and _auth_enabled():
                st.text_input(label, value=current, key=f"f_{key}", disabled=True,
                              help="Email is locked — contact your admin to change it.")
                new_values[key] = current  # preserve unchanged value
            elif kind == "textarea":
                new_values[key] = st.text_area(label, value=current, key=f"f_{key}")
            else:
                new_values[key] = st.text_input(label, value=current, key=f"f_{key}")
        submitted = st.form_submit_button("Save changes", use_container_width=True)

    if submitted:
        changes = {
            k: (person.get(k) or "", (v or "").strip())
            for k, v in new_values.items()
            if (person.get(k) or "") != (v or "").strip()
        }
        if not changes:
            st.info("Nothing changed.")
        else:
            update_payload = {k: (new or None) for k, (_, new) in changes.items()}
            uid = _current_auth_uid()
            try:
                sb.table("people").update(update_payload).eq("id", person["id"]).execute()
                log_rows = [
                    {
                        "person_id": person["id"],
                        "changed_by": uid,
                        "changed_by_email": current_user_email() or "demo",
                        "field_name": field,
                        "old_value": str(old) if old else None,
                        "new_value": str(new) if new else None,
                        "source": "worker" if _auth_enabled() else "system",
                    }
                    for field, (old, new) in changes.items()
                ]
                # Use service-role for change-log insert so it works in both modes
                # (RLS requires changed_by=auth.uid() but demo has no session).
                sb_admin.table("people_change_log").insert(log_rows).execute()
                st.success(f"Updated {len(changes)} field(s). Your admin has been notified.")
                st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Could not save: {e}")


# --------------------------------------------------------------------------
# Training records + certificate upload
# --------------------------------------------------------------------------
st.markdown("### My training records")

if not records_raw:
    st.info("No training records yet. Your admin will add these.")
    st.stop()

status_pill = {
    "none": ("No certificate", "#64748B"),
    "pending": ("Pending review", "#D97706"),
    "approved": ("Approved", "#16A34A"),
    "rejected": ("Rejected", "#DC2626"),
}

for r in sorted(records_raw, key=lambda x: types.get(x["training_type_id"], "")):
    name = types.get(r["training_type_id"], "—")
    exp = date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None
    comp = date.fromisoformat(r["completed_date"]) if r.get("completed_date") else None
    if exp:
        window = classify_window(exp, today=today)
        status = {"expired": "Expired", "7": "≤ 7 days", "30": "≤ 30 days", "90": "≤ 90 days"}.get(
            window, "In date"
        )
    elif comp:
        status = "Lifetime"
    else:
        status = "—"

    cert_label, cert_colour = status_pill.get(r.get("certificate_status") or "none", status_pill["none"])

    with st.expander(f"{name}  ·  {status}  ·  Cert: {cert_label}", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Completed:** {comp or '—'}")
            st.write(f"**Expires:** {exp or '—'}")
        with c2:
            st.markdown(
                f"<span style='color:{cert_colour};font-weight:600'>{cert_label}</span>",
                unsafe_allow_html=True,
            )
            if r.get("certificate_status") == "rejected" and r.get("certificate_reject_reason"):
                st.caption(f"Reason: {r['certificate_reject_reason']}")

        if r.get("certificate_status") == "pending":
            st.info("Your certificate is awaiting admin review. You'll see it here once approved.")
        else:
            upload = st.file_uploader(
                "Upload certificate (PDF, JPG, PNG)",
                type=["pdf", "jpg", "jpeg", "png"],
                key=f"up_{r['id']}",
            )
            if upload is not None and st.button("Submit for review", key=f"sub_{r['id']}"):
                # Path MUST be {person_id}/{training_record_id}/{filename}
                # to satisfy storage RLS policy certs_worker_upload (folder[1] = person_id).
                path = f"{person['id']}/{r['id']}/{upload.name}"
                uid = _current_auth_uid()
                try:
                    sb.storage.from_("certificates").upload(
                        path,
                        upload.getvalue(),
                        {"content-type": upload.type, "upsert": "true"},
                    )
                    update_payload = {
                        "certificate_url": path,
                        "certificate_status": "pending",
                        "certificate_uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "certificate_reject_reason": None,
                    }
                    if uid:
                        update_payload["certificate_uploaded_by"] = uid
                    sb.table("training_records").update(update_payload).eq(
                        "id", r["id"]
                    ).execute()
                    sb_admin.table("people_change_log").insert(
                        {
                            "person_id": person["id"],
                            "changed_by": uid,
                            "changed_by_email": current_user_email() or "demo",
                            "field_name": f"certificate:{name}",
                            "old_value": r.get("certificate_status") or "none",
                            "new_value": "pending",
                            "source": "worker" if _auth_enabled() else "system",
                        }
                    ).execute()
                    st.success("Certificate submitted. Your admin will review it.")
                    st.rerun()
                except Exception as e:  # noqa: BLE001
                    st.error(f"Upload failed: {e}")

help_box(
    "How this works",
    "Edits to your details save instantly and are sent to your admin as an audit trail. "
    "Certificate uploads sit in a review queue — once approved, the record updates "
    "and counts toward your compliance score.",
)
