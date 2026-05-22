from datetime import date

import pandas as pd
import streamlit as st

from app.auth import require_auth
from app.branding import help_box, inject_css, kpi_row, page_header
from beacon.db import anon_client
from beacon.reminders import classify_window

require_auth()
inject_css()
page_header("Dashboard", "Live training-expiry view across all active people and training types.")
help_box(
    "What you're looking at",
    "Counts of training records grouped by how close they are to expiring. "
    "Click any column header in the table below to sort. The same data drives the "
    "daily reminder email — anything in the red, orange, or yellow tiles is in the next digest.",
)

sb = anon_client()
records = sb.rpc("get_active_training_records").execute().data or []

rows = []
for r in records:
    if not r["expiry_date"]:
        continue
    exp = date.fromisoformat(r["expiry_date"])
    window = classify_window(exp, today=date.today())
    if window is None:
        continue
    rows.append({
        "Person": r["person_name"],
        "Training": r["training_name"],
        "Expires": exp,
        "Window": {"expired": "Expired", "7": "≤ 7 days", "30": "≤ 30 days", "90": "≤ 90 days"}[window],
        "_w": window,
    })

df = pd.DataFrame(rows)


def n(w: str) -> int:
    return int((df["_w"] == w).sum()) if not df.empty else 0


total = len(df)
kpi_row([
    {"label": "Expired", "value": n("expired"), "sub": "Overdue — action required", "tone": "expired"},
    {"label": "≤ 7 days", "value": n("7"), "sub": "Renew this week", "tone": "week"},
    {"label": "≤ 30 days", "value": n("30"), "sub": "Plan renewal", "tone": "month"},
    {"label": "≤ 90 days", "value": n("90"), "sub": "On the horizon", "tone": "quarter"},
])

if df.empty:
    st.success("Everything is in date for the next 90 days. Nothing to action.")
else:
    st.markdown(f"#### {total} record{'s' if total != 1 else ''} need attention")
    display = df.drop(columns=["_w"]).sort_values("Expires").reset_index(drop=True)
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Expires": st.column_config.DateColumn("Expires", format="DD MMM YYYY"),
            "Window": st.column_config.TextColumn("Status"),
        },
    )
