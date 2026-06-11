from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.auth import require_auth
from app.branding import inject_css, kpi_row, page_header, page_tour
from beacon.db import anon_client
from beacon.reminders import classify_window, compliance_summary

require_auth()
inject_css()
page_header("Dashboard", "Workforce compliance at a glance.")
page_tour(
    "dashboard",
    "This is the team's report card — the big picture in one look.",
    [
        ("The dial is like a fuel gauge",
         "The closer to 100%, the better the team is doing."),
        ("The four cards count the problems",
         "<b>Expired</b> means overdue right now. The other cards show what's "
         "coming up soon."),
        ("The list shows who to chase",
         "Most urgent at the top. Start there!"),
    ],
)

sb = anon_client()
records_raw = sb.rpc("get_active_training_records").execute().data or []

records = []
for r in records_raw:
    expiry = date.fromisoformat(r["expiry_date"]) if r["expiry_date"] else None
    records.append({**r, "expiry_date": expiry})

today = date.today()
summary = compliance_summary(records, today=today)
score = summary["score"]
total = summary["total"] or 1

# ── score thresholds
if score >= 90:
    score_colour, score_label = "#16A34A", "Excellent"
elif score >= 75:
    score_colour, score_label = "#16A34A", "Good"
elif score >= 50:
    score_colour, score_label = "#D97706", "Attention"
else:
    score_colour, score_label = "#DC2626", "At Risk"

# ── Gauge chart
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score,
    number={
        "suffix": "%",
        "font": {"size": 56, "color": score_colour, "family": "Inter, sans-serif"},
        "valueformat": ".0f",
    },
    gauge={
        "axis": {
            "range": [0, 100],
            "tickwidth": 1,
            "tickcolor": "#CBD5E1",
            "tickfont": {"size": 10, "color": "#94A3B8"},
            "dtick": 25,
        },
        "bar": {"color": score_colour, "thickness": 0.3},
        "bgcolor": "#F8FAFC",
        "borderwidth": 1,
        "bordercolor": "#E2E8F0",
        "steps": [
            {"range": [0,  50],  "color": "rgba(220,38,38,0.07)"},
            {"range": [50, 75],  "color": "rgba(217,119,6,0.06)"},
            {"range": [75, 90],  "color": "rgba(22,163,74,0.04)"},
            {"range": [90, 100], "color": "rgba(22,163,74,0.09)"},
        ],
        "threshold": {
            "line": {"color": score_colour, "width": 3},
            "thickness": 0.78,
            "value": score,
        },
    },
    title={
        "text": (
            f"<b style='color:{score_colour}'>{score_label}</b><br>"
            f"<span style='font-size:12px;color:#94A3B8'>Compliance Score</span>"
        ),
        "font": {"family": "Inter, sans-serif", "size": 18},
    },
))
gauge_fig.update_layout(
    paper_bgcolor="white",
    font={"color": "#334155", "family": "Inter, sans-serif"},
    height=290,
    margin=dict(l=30, r=30, t=90, b=10),
)

# ── Stacked distribution bar
dist_data = [
    ("Expired",   summary["expired"],  "#DC2626"),
    ("≤ 7 days",  summary["week"],     "#EA580C"),
    ("≤ 30 days", summary["month"],    "#D97706"),
    ("≤ 90 days", summary["quarter"],  "#3B82F6"),
    ("In date",   summary["safe"],     "#16A34A"),
]
dist_fig = go.Figure()
for label, val, colour in dist_data:
    dist_fig.add_trace(go.Bar(
        name=label,
        x=[val],
        y=[""],
        orientation="h",
        marker_color=colour,
        marker_line_width=0,
        text=f"<b>{val}</b>" if val > 0 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont={"color": "white", "size": 11, "family": "Inter, sans-serif"},
        hovertemplate=f"<b>{label}</b>: {val}<extra></extra>",
    ))
dist_fig.update_layout(
    barmode="stack",
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=92,
    margin=dict(l=2, r=2, t=4, b=48),
    legend=dict(
        orientation="h",
        y=-0.9,
        x=0,
        font={"size": 11, "color": "#64748B", "family": "Inter, sans-serif"},
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        itemsizing="constant",
    ),
    xaxis={"showgrid": False, "showticklabels": False, "zeroline": False, "showline": False},
    yaxis={"showgrid": False, "showticklabels": False, "showline": False},
    showlegend=True,
)

# ── Layout: gauge | KPI tiles + distribution
col_gauge, col_kpis = st.columns([1, 1.55])

with col_gauge:
    with st.container(border=True):
        st.plotly_chart(
            gauge_fig, use_container_width=True, config={"displayModeBar": False}
        )

with col_kpis:
    kpi_row([
        {"label": "Expired",   "value": summary["expired"],  "sub": "Overdue — act now",   "tone": "expired"},
        {"label": "≤ 7 days",  "value": summary["week"],     "sub": "Renew this week",     "tone": "week"},
        {"label": "≤ 30 days", "value": summary["month"],    "sub": "Plan ahead",          "tone": "month"},
        {"label": "≤ 90 days", "value": summary["quarter"],  "sub": "On the horizon",      "tone": "quarter"},
    ])
    st.markdown(
        "<p style='font-size:0.7rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:0.1em;color:#94A3B8;margin:14px 0 2px;'>Record Distribution</p>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        dist_fig, use_container_width=True, config={"displayModeBar": False}
    )

# ── Attention table
rows = []
for r in records:
    if not r["expiry_date"]:
        continue
    window = classify_window(r["expiry_date"], today=today)
    if window is None:
        continue
    rows.append({
        "Person":   r["person_name"],
        "Training": r["training_name"],
        "Expires":  r["expiry_date"],
        "Status":   {
            "expired": "Expired",
            "7":       "≤ 7 days",
            "30":      "≤ 30 days",
            "90":      "≤ 90 days",
        }[window],
    })

if not rows:
    st.success("Nothing expiring in the next 90 days — fully compliant.")
else:
    df = pd.DataFrame(rows).sort_values("Expires").reset_index(drop=True)
    n = len(df)
    st.markdown(
        f"<h4 style='margin:28px 0 8px;color:var(--t1);'>"
        f"{n} record{'s' if n != 1 else ''} need attention</h4>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Expires": st.column_config.DateColumn("Expires", format="DD MMM YYYY"),
        },
    )
