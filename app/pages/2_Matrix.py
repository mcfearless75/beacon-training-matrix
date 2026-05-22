from datetime import date

import pandas as pd
import streamlit as st

from app.auth import require_auth
from app.branding import colour_legend, help_box, inject_css, page_header
from beacon.db import anon_client
from beacon.reminders import classify_window

require_auth()
inject_css()
page_header(
    "Training Matrix",
    "Every person, every training type — coloured by time-to-expiry.",
)
help_box(
    "How to read this",
    "Each cell shows when a person's training expires. Cell colour shows urgency. "
    "Use the search and filter controls to narrow the view. Click <b>Edit a record</b> "
    "below the table to add or update one. Click <b>Bulk update</b> to mark several "
    "people complete at once after a training day.",
)
colour_legend()

sb = anon_client()
people = sb.table("people").select("id, name, job_title").eq("active", True).order("name").execute().data
types = sb.table("training_types").select("id, name").eq("active", True).order("name").execute().data
records = (
    sb.table("training_records")
    .select("person_id, training_type_id, expiry_date, completed_date, notes")
    .execute()
    .data
)
rec_by_pair = {(r["person_id"], r["training_type_id"]): r for r in records}

# ===== Filter bar =====
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    search = st.text_input(
        "Search",
        placeholder="Filter by person name or job title…",
        label_visibility="collapsed",
    ).strip().lower()
with f2:
    status_filter = st.selectbox(
        "Status filter",
        options=["All statuses", "Needs attention (≤90 days)", "Expired only", "≤30 days", "In date only"],
        label_visibility="collapsed",
    )
with f3:
    type_filter = st.multiselect(
        "Training type filter",
        options=[t["name"] for t in types],
        placeholder="All training types",
        label_visibility="collapsed",
    )


def colour(window):
    return {
        "expired": "#e57373", "7": "#e57373",
        "30": "#ffb74d", "90": "#fff176",
        None: "#a5d6a7",
    }.get(window, "#e0e0e0")


def row_passes_filter(p, row_records_for_person):
    """Returns True if this person row should appear given current filters."""
    if search:
        haystack = f"{p['name']} {p.get('job_title') or ''}".lower()
        if search not in haystack:
            return False
    if status_filter == "All statuses":
        return True
    # Otherwise, person must have at least one record matching the status filter
    today = date.today()
    for rec in row_records_for_person:
        if not rec or not rec.get("expiry_date"):
            continue
        exp = date.fromisoformat(rec["expiry_date"]) if isinstance(rec["expiry_date"], str) else rec["expiry_date"]
        window = classify_window(exp, today=today)
        if status_filter == "Expired only" and window == "expired":
            return True
        if status_filter == "≤30 days" and window in ("expired", "7", "30"):
            return True
        if status_filter == "Needs attention (≤90 days)" and window is not None:
            return True
        if status_filter == "In date only" and window is None:
            return True
    return status_filter == "In date only" and not row_records_for_person


# Filter visible types
visible_types = [t for t in types if not type_filter or t["name"] in type_filter]

# Build dataframe with filtering
columns = ["Person"] + [t["name"] for t in visible_types]
data, styles = [], []
for p in people:
    person_recs = [rec_by_pair.get((p["id"], t["id"])) for t in visible_types]
    if not row_passes_filter(p, person_recs):
        continue
    row = {"Person": p["name"]}
    row_styles = {"Person": ""}
    for t in visible_types:
        rec = rec_by_pair.get((p["id"], t["id"]))
        if rec and rec["expiry_date"]:
            exp = date.fromisoformat(rec["expiry_date"]) if isinstance(rec["expiry_date"], str) else rec["expiry_date"]
            row[t["name"]] = exp.strftime("%d %b %Y")
            window = classify_window(exp, today=date.today())
            row_styles[t["name"]] = f"background-color: {colour(window)}"
        elif rec and rec.get("completed_date"):
            row[t["name"]] = "Lifetime"
            row_styles[t["name"]] = "background-color: #cfd8dc"
        else:
            row[t["name"]] = ""
            row_styles[t["name"]] = ""
    data.append(row)
    styles.append(row_styles)

if not data:
    st.info("No rows match your filters. Try clearing the search or status filter.")
else:
    df = pd.DataFrame(data, columns=columns)

    def styler(_):
        return pd.DataFrame(styles, columns=columns)

    st.caption(f"Showing **{len(data)}** of **{len(people)}** people · **{len(visible_types)}** training types")
    st.dataframe(df.style.apply(styler, axis=None), use_container_width=True, hide_index=True)

st.divider()

# ===== Edit single record / Bulk update tabs =====
edit_tab, bulk_tab = st.tabs(["✎ Edit a record", "⚡ Bulk update"])

with edit_tab:
    if not people or not types:
        st.info("Add people and training types first.")
    else:
        person = st.selectbox("Person", options=people, format_func=lambda p: p["name"], key="edit_person")
        ttype = st.selectbox("Training type", options=types, format_func=lambda t: t["name"], key="edit_type")
        existing = rec_by_pair.get((person["id"], ttype["id"]))
        completed = st.date_input(
            "Completed date",
            value=date.fromisoformat(existing["completed_date"]) if existing and existing.get("completed_date") else None,
            key="edit_completed",
        )
        expiry = st.date_input(
            "Expiry date (leave blank for lifetime)",
            value=date.fromisoformat(existing["expiry_date"]) if existing and existing.get("expiry_date") else None,
            key="edit_expiry",
        )
        notes = st.text_input("Notes", value=(existing or {}).get("notes") or "", key="edit_notes")
        if st.button("Save", key="edit_save"):
            sb.table("training_records").upsert(
                {
                    "person_id": person["id"],
                    "training_type_id": ttype["id"],
                    "completed_date": completed.isoformat() if completed else None,
                    "expiry_date": expiry.isoformat() if expiry else None,
                    "notes": notes or None,
                },
                on_conflict="person_id,training_type_id",
            ).execute()
            st.success("Saved.")
            st.rerun()

with bulk_tab:
    st.caption("Mark **multiple people** complete on the **same training type** at once. Ideal after a training day.")
    if not people or not types:
        st.info("Add people and training types first.")
    else:
        bulk_type = st.selectbox("Training type", options=types, format_func=lambda t: t["name"], key="bulk_type")
        bulk_people = st.multiselect(
            "People to update",
            options=people,
            format_func=lambda p: p["name"],
            placeholder="Select people from the list",
            key="bulk_people",
        )
        b1, b2 = st.columns(2)
        with b1:
            bulk_completed = st.date_input("Completed on", value=date.today(), key="bulk_completed")
        with b2:
            bulk_expiry = st.date_input("Expires on (blank = lifetime)", value=None, key="bulk_expiry")
        bulk_notes = st.text_input("Notes (applied to all)", key="bulk_notes")

        if st.button(f"Mark {len(bulk_people)} people complete", disabled=not bulk_people, key="bulk_save"):
            payload = [
                {
                    "person_id": p["id"],
                    "training_type_id": bulk_type["id"],
                    "completed_date": bulk_completed.isoformat() if bulk_completed else None,
                    "expiry_date": bulk_expiry.isoformat() if bulk_expiry else None,
                    "notes": bulk_notes or None,
                }
                for p in bulk_people
            ]
            sb.table("training_records").upsert(payload, on_conflict="person_id,training_type_id").execute()
            st.success(f"Updated {len(bulk_people)} records.")
            st.rerun()
