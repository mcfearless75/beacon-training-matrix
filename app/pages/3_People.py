import streamlit as st

from app.auth import require_auth
from app.branding import help_box, inject_css, page_header
from beacon.db import anon_client

require_auth()
inject_css()
page_header("People", "Add, edit, and manage workforce records.")
help_box(
    "Managing people",
    "Add new starters with the form below, or click any name to expand and edit. "
    "Set someone to <b>inactive</b> when they leave — they'll be hidden from the Matrix "
    "and Dashboard but their history is preserved.",
)
sb = anon_client()

with st.expander("Add new person"):
    name = st.text_input("Name", key="new_name")
    job_title = st.text_input("Job title", key="new_job")
    paye = st.checkbox("PAYE", key="new_paye")
    ni = st.text_input("NI number", key="new_ni")
    start = st.date_input("Start date", value=None, key="new_start")
    if st.button("Add", key="add_person") and name:
        sb.table("people").insert({
            "name": name,
            "job_title": job_title or None,
            "paye": paye,
            "ni_number": ni or None,
            "start_date": start.isoformat() if start else None,
        }).execute()
        st.success("Added.")
        st.rerun()

people = sb.table("people").select("*").order("name").execute().data
active_count = sum(1 for p in people if p.get("active"))
st.caption(f"**{active_count} active** · {len(people)} total")

for p in people:
    with st.expander(f"{p['name']} {'(inactive)' if not p['active'] else ''}"):
        new_title = st.text_input("Job title", value=p.get("job_title") or "", key=f"jt_{p['id']}")
        new_active = st.checkbox("Active", value=p["active"], key=f"act_{p['id']}")
        if st.button("Save", key=f"sv_{p['id']}"):
            sb.table("people").update(
                {"job_title": new_title or None, "active": new_active}
            ).eq("id", p["id"]).execute()
            st.success("Saved.")
            st.rerun()
