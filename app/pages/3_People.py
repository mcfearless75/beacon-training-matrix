from datetime import date

import streamlit as st

from app.auth import require_auth
from app.branding import help_box, inject_css, page_header
from beacon.db import anon_client
from beacon.reminders import compliance_summary

require_auth()
inject_css()
page_header("People", "Add, edit, and manage workforce records.")
help_box(
    "Managing people",
    "Add new starters with the form below. Click any name to expand and edit their details. "
    "Set someone to <b>inactive</b> to remove them from the Matrix — their training history is preserved.",
)

sb = anon_client()

# ===== Add new person =====
with st.expander("Add new person", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        new_name = st.text_input("Full name *", key="new_name")
        new_job = st.text_input("Job title", key="new_job")
        new_paye = st.checkbox("PAYE employee", key="new_paye")
    with c2:
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
            # Compliance badge strip
            st.markdown(
                f'<div style="margin-bottom:14px;">'
                f'<span class="compliance-badge {tone}">{badge_text}</span>'
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

            btn_col, link_col = st.columns([1, 1])
            with btn_col:
                if st.button("Save changes", key=f"sv_{tab_key}_{p['id']}", type="primary"):
                    sb.table("people").update({
                        "job_title": new_title.strip() or None,
                        "ni_number": new_ni.strip() or None,
                        "paye": new_paye,
                        "start_date": new_start.isoformat() if new_start else None,
                        "active": new_active,
                    }).eq("id", p["id"]).execute()
                    st.success("Saved.")
                    st.rerun()
            with link_col:
                try:
                    st.page_link("pages/7_Profile.py", label="View full profile →")
                except Exception:
                    st.caption("See Profile page for full detail.")


with tab_active:
    _render_people(active_list, "act")

with tab_inactive:
    _render_people(inactive_list, "inact")
