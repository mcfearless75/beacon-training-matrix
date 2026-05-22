from datetime import date

import pandas as pd
import streamlit as st

from app.auth import require_auth
from beacon.db import anon_client
from beacon.reminders import classify_window

require_auth()
st.title("Dashboard")

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
        "Window": {"expired": "Expired", "7": "≤7 days", "30": "≤30 days", "90": "≤90 days"}[window],
        "_w": window,
    })

df = pd.DataFrame(rows)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Expired", (df["_w"] == "expired").sum() if not df.empty else 0)
c2.metric("≤ 7 days", (df["_w"] == "7").sum() if not df.empty else 0)
c3.metric("≤ 30 days", (df["_w"] == "30").sum() if not df.empty else 0)
c4.metric("≤ 90 days", (df["_w"] == "90").sum() if not df.empty else 0)

if df.empty:
    st.info("Nothing expiring in the next 90 days.")
else:
    st.dataframe(df.drop(columns=["_w"]).sort_values("Expires"), use_container_width=True)
