import streamlit as st

from app.auth import require_admin
from app.branding import inject_css, page_header
from beacon.db import anon_client

require_admin()
inject_css()
page_header("Training Types", "The catalogue of qualifications and certifications tracked.")
sb = anon_client()

with st.expander("Add new training type"):
    name = st.text_input("Name")
    code = st.text_input("Code (optional, e.g. A, B, C)")
    notes = st.text_area("Notes")
    if st.button("Add") and name:
        sb.table("training_types").insert({
            "name": name,
            "code": code or None,
            "notes": notes or None,
        }).execute()
        st.success("Added.")
        st.rerun()

types = sb.table("training_types").select("*").order("name").execute().data
for t in types:
    with st.expander(f"{t['name']} {'(inactive)' if not t['active'] else ''}"):
        active = st.checkbox("Active", value=t["active"], key=f"act_{t['id']}")
        notes = st.text_area("Notes", value=t.get("notes") or "", key=f"nt_{t['id']}")
        if st.button("Save", key=f"sv_{t['id']}"):
            sb.table("training_types").update(
                {"active": active, "notes": notes or None}
            ).eq("id", t["id"]).execute()
            st.success("Saved.")
            st.rerun()
