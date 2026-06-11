from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from app.auth import require_auth
from app.branding import help_box, inject_css, page_header, page_tour
from beacon.db import anon_client
from beacon.reminders import classify_window

require_auth()
inject_css()
page_header(
    "Renewal Timeline",
    "See your training workload month by month for the year ahead.",
)
page_tour(
    "timeline",
    "What needs renewing, month by month, for the year ahead.",
    [
        ("Read it like a calendar",
         "Each month shows the courses that run out then."),
        ("Plan ahead",
         "See a busy month coming? Book the courses early and spread the load."),
    ],
)
help_box(
    "Plan your training calendar",
    "Each bar shows how many training renewals fall due in that month. "
    "Use it to spread training events across the year — and to spot months "
    "with heavy renewal clusters that need scheduling now.",
)

sb = anon_client()
records = sb.rpc("get_active_training_records").execute().data or []

today = date.today()
horizon_end = today + timedelta(days=365)

# Bucket by year-month
buckets: dict[str, dict] = defaultdict(lambda: {"count": 0, "expired": 0, "items": []})
for r in records:
    if not r["expiry_date"]:
        continue
    exp = date.fromisoformat(r["expiry_date"])
    if exp < today - timedelta(days=60) or exp > horizon_end:
        continue
    key = exp.strftime("%Y-%m")
    label = exp.strftime("%b %Y")
    buckets[key]["label"] = label
    buckets[key]["count"] += 1
    if exp <= today:
        buckets[key]["expired"] += 1
    buckets[key]["items"].append(
        {"date": exp, "person": r["person_name"], "training": r["training_name"]}
    )

# Sorted months
sorted_keys = sorted(buckets.keys())
if not sorted_keys:
    st.info("No upcoming renewals in the next 12 months.")
    st.stop()

max_count = max(b["count"] for b in buckets.values()) or 1

# ===== Bar chart (HTML for full visual control) =====
bars_html_parts = []
for k in sorted_keys:
    b = buckets[k]
    height_pct = (b["count"] / max_count) * 100
    is_past = k <= today.strftime("%Y-%m") and b["expired"] > 0
    bar_colour = "#DC2626" if is_past else ("#EA580C" if b["count"] >= max_count * 0.7 else "#F4845F")
    label = b["label"]
    count = b["count"]
    expired_badge = (
        f'<div class="tl-expired-badge">{b["expired"]} overdue</div>'
        if b["expired"] > 0 else ""
    )
    bars_html_parts.append(
        '<div class="tl-col">'
        f'<div class="tl-count">{count}</div>'
        f'<div class="tl-bar-wrap"><div class="tl-bar" style="height:{height_pct:.1f}%; background:{bar_colour};"></div></div>'
        f'{expired_badge}'
        f'<div class="tl-month">{label}</div>'
        '</div>'
    )

st.markdown(
    f'<div class="timeline-card"><div class="tl-chart">{"".join(bars_html_parts)}</div></div>',
    unsafe_allow_html=True,
)

# ===== Selected-month detail =====
st.markdown("#### Renewals by month")
month_label_to_key = {buckets[k]["label"]: k for k in sorted_keys}
selected_label = st.selectbox(
    "Choose a month",
    options=list(month_label_to_key.keys()),
    label_visibility="collapsed",
)
selected_key = month_label_to_key[selected_label]
items = sorted(buckets[selected_key]["items"], key=lambda x: x["date"])
df = pd.DataFrame([
    {"Person": it["person"], "Training": it["training"], "Date": it["date"]}
    for it in items
])
st.dataframe(
    df, use_container_width=True, hide_index=True,
    column_config={"Date": st.column_config.DateColumn("Date", format="DD MMM YYYY")},
)
