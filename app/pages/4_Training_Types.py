import streamlit as st

from app.auth import require_admin
from app.branding import help_box, inject_css, page_header
from beacon.db import anon_client

require_admin()
inject_css()
page_header("Training Types", "The catalogue of qualifications and certifications tracked.")
help_box(
    "What goes here",
    "Add every kind of training, ticket, or certificate you track. "
    "These become the columns of the Matrix. Assign a <b>category</b> to group related types together "
    "(e.g. Core H&amp;S, First Aid, Site Operations). "
    "Use <b>Role Requirements</b> to mark which training is mandatory for each job title — "
    "the Matrix will flag anyone missing required training as <b>Required — Missing</b>.",
)

sb = anon_client()

_CATEGORIES = ["Core H&S", "First Aid", "Site Operations", "Plant & Equipment", "Specialist", "General"]

tab_types, tab_roles = st.tabs(["Training types", "Role requirements"])

# ===========================
with tab_types:
    with st.expander("Add new training type", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Name *", key="new_name")
            new_code = st.text_input("Short code (optional, e.g. FAW)", key="new_code")
        with c2:
            new_cat = st.selectbox("Category", options=_CATEGORIES, key="new_cat")
            new_notes = st.text_input("Notes", key="new_notes")
        if st.button("Add training type", key="add_type", type="primary"):
            if not new_name.strip():
                st.error("Name is required.")
            else:
                try:
                    sb.table("training_types").insert({
                        "name": new_name.strip(),
                        "code": new_code.strip() or None,
                        "category": new_cat,
                        "notes": new_notes.strip() or None,
                    }).execute()
                    st.success(f"Added '{new_name.strip()}'.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not add — {e}")

    types = sb.table("training_types").select("*").order("name").execute().data
    active_count = sum(1 for t in types if t.get("active"))
    st.caption(f"**{active_count} active** · {len(types)} total")

    for t in types:
        label = t["name"]
        if not t.get("active"):
            label += "  (inactive)"
        cat_label = t.get("category") or "General"
        label += f"  ·  {cat_label}"

        with st.expander(label):
            c1, c2 = st.columns(2)
            with c1:
                edit_name = st.text_input("Name", value=t["name"], key=f"en_{t['id']}")
                edit_code = st.text_input("Short code", value=t.get("code") or "", key=f"ec_{t['id']}")
            with c2:
                cat_idx = _CATEGORIES.index(t.get("category")) if t.get("category") in _CATEGORIES else len(_CATEGORIES) - 1
                edit_cat = st.selectbox("Category", options=_CATEGORIES, index=cat_idx, key=f"ecat_{t['id']}")
                edit_active = st.checkbox("Active", value=bool(t.get("active")), key=f"act_{t['id']}")
            edit_notes = st.text_input("Notes", value=t.get("notes") or "", key=f"nt_{t['id']}")
            if st.button("Save", key=f"sv_{t['id']}", type="primary"):
                sb.table("training_types").update({
                    "name": edit_name.strip() or t["name"],
                    "code": edit_code.strip() or None,
                    "category": edit_cat,
                    "active": edit_active,
                    "notes": edit_notes.strip() or None,
                }).eq("id", t["id"]).execute()
                st.success("Saved.")
                st.rerun()

# ===========================
with tab_roles:
    st.markdown(
        "Set which training types are **mandatory** for each job title. "
        "In the Matrix, people with that role who are missing required training will show a "
        "**Required — Missing** cell (red, bold) instead of a blank."
    )

    types_active = sb.table("training_types").select("id, name, category").eq("active", True).order("name").execute().data
    requirements_raw = sb.table("role_requirements").select("job_title, training_type_id").execute().data
    req_by_role: dict[str, list] = {}
    for r in requirements_raw:
        req_by_role.setdefault(r["job_title"], []).append(r["training_type_id"])

    # Distinct job titles from people
    people_raw = sb.table("people").select("job_title").eq("active", True).execute().data
    job_titles = sorted({p["job_title"] for p in people_raw if p.get("job_title")})

    if not job_titles:
        st.info("Add people with job titles on the People page first — job titles drive role requirements.")
    else:
        sel_role = st.selectbox("Job title to configure", options=job_titles, key="req_role")
        current_ids = req_by_role.get(sel_role, [])
        current_types = [t for t in types_active if t["id"] in current_ids]

        sel_req = st.multiselect(
            "Required training types for this role",
            options=types_active,
            default=current_types,
            format_func=lambda t: f"{t['name']}  ({t.get('category') or 'General'})",
            key="req_types",
        )
        if st.button("Save requirements", key="save_req", type="primary"):
            sb.table("role_requirements").delete().eq("job_title", sel_role).execute()
            if sel_req:
                sb.table("role_requirements").insert([
                    {"job_title": sel_role, "training_type_id": t["id"]} for t in sel_req
                ]).execute()
            st.success(f"Saved: {len(sel_req)} required types for '{sel_role}'.")
            st.rerun()

    # Summary of all configured requirements
    if req_by_role:
        st.divider()
        st.markdown("##### All configured requirements")
        type_name = {t["id"]: t["name"] for t in types_active}
        for role, tids in sorted(req_by_role.items()):
            names = ", ".join(sorted(type_name.get(tid, "?") for tid in tids))
            st.markdown(f"**{role}** — {names}")
