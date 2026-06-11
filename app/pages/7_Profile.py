from datetime import date

import pandas as pd
import streamlit as st

from app.auth import require_auth
from app.branding import help_box, inject_css, page_header, page_tour
from beacon.db import anon_client
from beacon.reminders import classify_window, compliance_summary

require_auth()
inject_css()
page_header(
    "Person Profile",
    "Drill into one person's full training history and renewals.",
)
page_tour(
    "person_profile",
    "A deep dive on one person at a time.",
    [
        ("Pick a person",
         "Choose a name at the top — everything below changes to show just them."),
        ("Their full history",
         "Every course they've done and when each one runs out, all in one place."),
    ],
)

sb = anon_client()
people = sb.table("people").select("*").eq("active", True).order("name").execute().data
types = {t["id"]: t["name"] for t in sb.table("training_types").select("id, name").execute().data}

if not people:
    st.info("Add a person on the People page first.")
    st.stop()

selected = st.selectbox("Choose a person", options=people, format_func=lambda p: p["name"])

# Identity card
ident_html = (
    '<div class="profile-card">'
    f'<div class="profile-avatar">{(selected["name"][:1] or "?").upper()}</div>'
    '<div class="profile-meta">'
    f'<div class="profile-name">{selected["name"]}</div>'
    f'<div class="profile-job">{selected.get("job_title") or "—"}</div>'
    f'<div class="profile-start">Joined: {selected.get("start_date") or "—"}'
    f'{" · PAYE" if selected.get("paye") else ""}</div>'
    '</div></div>'
)
st.markdown(ident_html, unsafe_allow_html=True)

# Fetch this person's records
records_raw = (
    sb.table("training_records")
    .select("training_type_id, completed_date, expiry_date, notes")
    .eq("person_id", selected["id"])
    .execute()
    .data
    or []
)

# Compliance summary just for them
records_for_calc = []
for r in records_raw:
    exp = date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None
    records_for_calc.append({"expiry_date": exp})

today = date.today()
summary = compliance_summary(records_for_calc, today=today)

score_colour = "#16A34A" if summary["score"] >= 75 else "#D97706" if summary["score"] >= 50 else "#DC2626"
score_label = "Compliant" if summary["score"] >= 90 else "Needs attention" if summary["score"] < 75 else "Mostly compliant"

mini_html = (
    '<div class="profile-stats">'
    '<div class="profile-stat">'
    f'<div class="ps-value" style="color:{score_colour};">{summary["score"]}%</div>'
    f'<div class="ps-label">Compliance · {score_label}</div></div>'
    '<div class="profile-stat">'
    f'<div class="ps-value" style="color:#DC2626;">{summary["expired"]}</div>'
    '<div class="ps-label">Expired</div></div>'
    '<div class="profile-stat">'
    f'<div class="ps-value" style="color:#D97706;">{summary["week"] + summary["month"]}</div>'
    '<div class="ps-label">Due ≤30 days</div></div>'
    '<div class="profile-stat">'
    f'<div class="ps-value">{len(records_raw)}</div>'
    '<div class="ps-label">Total records</div></div>'
    '</div>'
)
st.markdown(mini_html, unsafe_allow_html=True)

help_box(
    "About this profile",
    "Compliance score is this person's individual percentage of records that are not "
    "expired and not due within 7 days. Use the table below to see every record, "
    "or jump to the Matrix to make changes.",
)

# Records table
if not records_raw:
    st.info("No training records for this person yet. Add one on the Matrix page.")
else:
    rows = []
    for r in records_raw:
        exp = date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None
        comp = date.fromisoformat(r["completed_date"]) if r.get("completed_date") else None
        if exp:
            window = classify_window(exp, today=today)
            status = {"expired": "Expired", "7": "≤ 7 days", "30": "≤ 30 days", "90": "≤ 90 days"}.get(window, "In date")
        elif comp:
            status = "Lifetime"
        else:
            status = "—"
        rows.append({
            "Training": types.get(r["training_type_id"], "—"),
            "Completed": comp,
            "Expires": exp,
            "Status": status,
            "Notes": r.get("notes") or "",
        })
    df = pd.DataFrame(rows).sort_values(["Status", "Expires"], na_position="last")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Completed": st.column_config.DateColumn("Completed", format="DD MMM YYYY"),
            "Expires": st.column_config.DateColumn("Expires", format="DD MMM YYYY"),
        },
    )
