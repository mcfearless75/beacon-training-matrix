from datetime import date, datetime, timezone

import streamlit as st

from app.auth import current_user_email, get_session, require_admin
from beacon.approvals import is_expiry_in_past, validate_approval
from app.branding import help_box, inject_css, page_header, page_tour
from beacon.db import service_client

require_admin()
inject_css()
page_header("Approvals", "Review certificates uploaded by workers.")
page_tour(
    "approvals",
    "Certificates your team uploaded, waiting for your thumbs-up.",
    [
        ("Open one",
         "Click an item to see the certificate that was uploaded."),
        ("Looks right? Approve it",
         "Press <b>Approve</b> and the record turns valid straight away."),
        ("Looks wrong? Reject it",
         "Press <b>Reject</b> and write a short note so the person knows what to fix."),
    ],
)
help_box(
    "Reviewing certificates",
    "Workers upload certificates from their My Profile page. Each upload lands here "
    "as <b>pending</b>. Approve to mark the record valid, or reject with a reason so "
    "the worker knows what to fix. Every decision is logged.",
)

sb = service_client()  # admin page — service role bypasses RLS; gated by require_admin()


def _signed_url(path: str | None) -> str | None:
    """Generate a short-lived signed URL for a certificate stored in the
    'certificates' bucket. Returns None if no path."""
    if not path:
        return None
    try:
        res = sb.storage.from_("certificates").create_signed_url(path, 600)
        return res.get("signedURL") or res.get("signed_url")
    except Exception:
        return None


# ===== Load pending queue =====
pending = (
    sb.table("training_records")
    .select(
        "id, person_id, training_type_id, completed_date, expiry_date, "
        "certificate_url, certificate_status, certificate_uploaded_at, "
        "certificate_uploaded_by"
    )
    .eq("certificate_status", "pending")
    .order("certificate_uploaded_at", desc=False)
    .execute()
    .data
    or []
)

# Hydrate person + training type names in one shot each
person_ids = list({r["person_id"] for r in pending})
type_ids = list({r["training_type_id"] for r in pending})

people_by_id: dict[str, dict] = {}
if person_ids:
    people_by_id = {
        p["id"]: p
        for p in sb.table("people").select("id, name, job_title").in_("id", person_ids).execute().data
    }

types_by_id: dict[str, dict] = {}
if type_ids:
    types_by_id = {
        t["id"]: t
        for t in sb.table("training_types").select("id, name").in_("id", type_ids).execute().data
    }


# ===== Header stats =====
st.caption(f"**{len(pending)} pending** certificate{'s' if len(pending) != 1 else ''} awaiting review.")

if not pending:
    st.success("Nothing to review — the queue is clear.")
else:
    for rec in pending:
        person = people_by_id.get(rec["person_id"], {})
        ttype = types_by_id.get(rec["training_type_id"], {})
        person_name = person.get("name") or "Unknown worker"
        type_name = ttype.get("name") or "Unknown training"
        uploaded_at = rec.get("certificate_uploaded_at")
        if uploaded_at:
            try:
                uploaded_at_fmt = datetime.fromisoformat(uploaded_at.replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M")
            except Exception:
                uploaded_at_fmt = uploaded_at
        else:
            uploaded_at_fmt = "—"

        expiry = rec.get("expiry_date")
        expiry_fmt = "—"
        if expiry:
            try:
                exp = date.fromisoformat(expiry)
                expiry_fmt = exp.strftime("%d %b %Y")
            except Exception:
                expiry_fmt = expiry

        label = f"{person_name}  ·  {type_name}  ·  uploaded {uploaded_at_fmt}"
        with st.expander(label, expanded=False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(
                    f"**Worker:** {person_name}  \n"
                    f"**Job title:** {person.get('job_title') or '—'}  \n"
                    f"**Training:** {type_name}  \n"
                    f"**Completed:** {rec.get('completed_date') or '—'}  \n"
                    f"**Expires:** {expiry_fmt}"
                )
                signed = _signed_url(rec.get("certificate_url"))
                if signed:
                    st.link_button("Open certificate", signed, use_container_width=False)
                else:
                    st.caption("No certificate file attached.")

            with col2:
                prefill_expiry = None
                if rec.get("expiry_date"):
                    try:
                        prefill_expiry = date.fromisoformat(rec["expiry_date"])
                    except Exception:
                        prefill_expiry = None

                is_lifetime = st.checkbox(
                    "No expiry (lifetime cert)",
                    key=f"lifetime_{rec['id']}",
                )
                new_expiry = st.date_input(
                    "New expiry date",
                    key=f"expiry_{rec['id']}",
                    value=prefill_expiry,
                    disabled=is_lifetime,
                )
                if not is_lifetime and is_expiry_in_past(new_expiry, today=date.today()):
                    st.caption("⚠️ This date is already expired — is that right?")

                reject_key = f"reject_reason_{rec['id']}"
                reason = st.text_area(
                    "Rejection reason (required to reject)",
                    key=reject_key,
                    height=100,
                    placeholder="e.g. Expired certificate, wrong worker, illegible scan…",
                )

                approve_col, reject_col = st.columns(2)
                with approve_col:
                    if st.button("Approve", key=f"approve_{rec['id']}", type="primary", use_container_width=True):
                        error = validate_approval(None if is_lifetime else new_expiry, is_lifetime)
                        if error:
                            st.error(error)
                        else:
                            session = get_session()
                            reviewer_id = session.user.id if session and getattr(session, "user", None) else None
                            try:
                                sb.table("training_records").update({
                                    "certificate_status": "approved",
                                    "certificate_reviewed_at": datetime.now(timezone.utc).isoformat(),
                                    "certificate_reviewed_by": reviewer_id,
                                    "certificate_reject_reason": None,
                                    "expiry_date": None if is_lifetime else new_expiry.isoformat(),
                                }).eq("id", rec["id"]).execute()
                                st.success(f"Approved certificate for {person_name}.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Could not approve — {e}")

                with reject_col:
                    if st.button("Reject", key=f"reject_{rec['id']}", use_container_width=True):
                        if not reason.strip():
                            st.error("Add a rejection reason first.")
                        else:
                            session = get_session()
                            reviewer_id = session.user.id if session and getattr(session, "user", None) else None
                            try:
                                sb.table("training_records").update({
                                    "certificate_status": "rejected",
                                    "certificate_reviewed_at": datetime.now(timezone.utc).isoformat(),
                                    "certificate_reviewed_by": reviewer_id,
                                    "certificate_reject_reason": reason.strip(),
                                }).eq("id", rec["id"]).execute()
                                st.success(f"Rejected certificate for {person_name}.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Could not reject — {e}")


# ===== Recent decisions =====
st.divider()
st.subheader("Recent decisions")
recent = (
    sb.table("certificate_review_log")
    .select("action, reviewed_at, reviewed_by_email, person_id, reject_reason")
    .order("reviewed_at", desc=True)
    .limit(20)
    .execute()
    .data
    or []
)

if not recent:
    st.caption("No reviews logged yet.")
else:
    recent_person_ids = list({r["person_id"] for r in recent if r.get("person_id")})
    recent_people: dict[str, str] = {}
    if recent_person_ids:
        recent_people = {
            p["id"]: p["name"]
            for p in sb.table("people").select("id, name").in_("id", recent_person_ids).execute().data
        }

    for entry in recent:
        when = entry.get("reviewed_at", "")
        try:
            when_fmt = datetime.fromisoformat(when.replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M")
        except Exception:
            when_fmt = when
        who = recent_people.get(entry.get("person_id"), "Unknown")
        reviewer = entry.get("reviewed_by_email") or "system"
        action = entry.get("action", "")
        reason = entry.get("reject_reason")
        suffix = f" — {reason}" if reason else ""
        tone = "green" if action == "approved" else "red"
        st.markdown(
            f'<div style="margin:6px 0;">'
            f'<span class="compliance-badge {tone}">{action.title()}</span> '
            f'<b>{who}</b> · {when_fmt} · by {reviewer}{suffix}'
            f'</div>',
            unsafe_allow_html=True,
        )
