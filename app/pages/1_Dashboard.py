from datetime import date

import pandas as pd
import streamlit as st

from app.auth import require_auth
from app.branding import help_box, inject_css, kpi_row, page_header
from beacon.db import anon_client
from beacon.reminders import classify_window, compliance_summary

require_auth()
inject_css()
page_header(
    "Dashboard",
    "Live training-expiry view across all active people and training types.",
)

sb = anon_client()
records_raw = sb.rpc("get_active_training_records").execute().data or []

records = []
for r in records_raw:
    if r["expiry_date"]:
        records.append({**r, "expiry_date": date.fromisoformat(r["expiry_date"])})
    else:
        records.append({**r, "expiry_date": None})

today = date.today()
summary = compliance_summary(records, today=today)
score = summary["score"]

# ===== Compliance score hero =====
if score >= 90:
    score_colour = "#16A34A"
    score_label = "Excellent"
    score_msg = "Your workforce is in great shape — nothing urgent."
elif score >= 75:
    score_colour = "#16A34A"
    score_label = "Good"
    score_msg = "Most records are in date. A few need attention soon."
elif score >= 50:
    score_colour = "#D97706"
    score_label = "Attention"
    score_msg = "Several records need renewing in the next week."
else:
    score_colour = "#DC2626"
    score_label = "At risk"
    score_msg = "Significant compliance gaps — review immediately."

# Build the bar visual (4 segments, weighted by counts)
total = summary["total"] or 1
seg_widths = [
    ("#DC2626", summary["expired"] / total * 100),
    ("#EA580C", summary["week"] / total * 100),
    ("#D97706", summary["month"] / total * 100),
    ("#16A34A", (summary["quarter"] + summary["safe"]) / total * 100),
]
bar_html = "".join(
    f'<div style="width:{w:.2f}%; background:{c};"></div>' for c, w in seg_widths
)

hero_html = (
    '<div class="compliance-hero">'
    '<div class="ch-left">'
    f'<div class="ch-score" style="color:{score_colour};">{score}<span>%</span></div>'
    f'<div class="ch-label">Compliance score</div>'
    '</div>'
    '<div class="ch-right">'
    f'<div class="ch-status" style="color:{score_colour};">{score_label}</div>'
    f'<div class="ch-msg">{score_msg}</div>'
    f'<div class="ch-bar">{bar_html}</div>'
    '<div class="ch-bar-key">'
    f'<span><b style="color:#DC2626;">●</b> Expired {summary["expired"]}</span>'
    f'<span><b style="color:#EA580C;">●</b> ≤7d {summary["week"]}</span>'
    f'<span><b style="color:#D97706;">●</b> ≤30d {summary["month"]}</span>'
    f'<span><b style="color:#16A34A;">●</b> In date {summary["quarter"] + summary["safe"]}</span>'
    '</div></div></div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

help_box(
    "What you're looking at",
    "Your <b>compliance score</b> is the percentage of training records that are not "
    "expired and not due within 7 days. The bar shows the distribution. Tiles below "
    "break it down by urgency. The table lists every record that needs attention.",
)

# ===== KPI tiles =====
kpi_row([
    {"label": "Expired", "value": summary["expired"], "sub": "Overdue — action required", "tone": "expired"},
    {"label": "≤ 7 days", "value": summary["week"], "sub": "Renew this week", "tone": "week"},
    {"label": "≤ 30 days", "value": summary["month"], "sub": "Plan renewal", "tone": "month"},
    {"label": "≤ 90 days", "value": summary["quarter"], "sub": "On the horizon", "tone": "quarter"},
])

# ===== Table of attention items =====
rows = []
for r in records:
    if not r["expiry_date"]:
        continue
    window = classify_window(r["expiry_date"], today=today)
    if window is None:
        continue
    rows.append({
        "Person": r["person_name"],
        "Training": r["training_name"],
        "Expires": r["expiry_date"],
        "Status": {"expired": "Expired", "7": "≤ 7 days", "30": "≤ 30 days", "90": "≤ 90 days"}[window],
    })

if not rows:
    st.success("Nothing expiring in the next 90 days. You're fully compliant.")
else:
    df = pd.DataFrame(rows).sort_values("Expires").reset_index(drop=True)
    st.markdown(f"#### {len(df)} record{'s' if len(df) != 1 else ''} need attention")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Expires": st.column_config.DateColumn("Expires", format="DD MMM YYYY"),
        },
    )
