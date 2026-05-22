from datetime import date

import streamlit as st

from app.auth import require_auth
from app.branding import help_box, inject_css, page_header
from beacon.db import anon_client
from beacon.reminders import classify_window, compliance_summary

require_auth()
inject_css()
page_header(
    "Audit Report",
    "Export a print-ready compliance report for CHAS, Constructionline, ISO 45001, and client submissions.",
)
help_box(
    "How to export as PDF",
    "Click <b>Generate report</b>, then <b>Download</b>. Open the downloaded .html file in any browser "
    "and press <b>Ctrl+P</b> (or ⌘+P on Mac) → choose <b>Save as PDF</b> as the destination. "
    "Landscape orientation works best for wide matrices.",
)

sb = anon_client()
people_all = sb.table("people").select("*").eq("active", True).order("name").execute().data
types_all = sb.table("training_types").select("id, name, category").eq("active", True).order("name").execute().data
records_all = sb.table("training_records").select("person_id, training_type_id, expiry_date, completed_date").execute().data
requirements_raw = sb.table("role_requirements").select("job_title, training_type_id").execute().data
rec_by_pair = {(r["person_id"], r["training_type_id"]): r for r in records_all}
req_by_role: dict[str, set] = {}
for r in requirements_raw:
    req_by_role.setdefault(r["job_title"], set()).add(r["training_type_id"])

# Sort types by category
sorted_types = sorted(types_all, key=lambda t: (t.get("category") or "General", t["name"]))

today = date.today()

# ===== Report options =====
c1, c2 = st.columns(2)
with c1:
    company_name = st.text_input("Organisation name", placeholder="e.g. Acme Construction Ltd", key="org_name")
    report_scope = st.radio("Report scope", ["Full workforce", "Single person"], horizontal=True)
with c2:
    selected_person = None
    if report_scope == "Single person":
        selected_person = st.selectbox("Choose person", options=people_all, format_func=lambda p: p["name"])
    include_req = st.checkbox("Highlight required — missing", value=True)
    include_scores = st.checkbox("Include compliance scores", value=True)

if not st.button("Generate report", type="primary"):
    st.stop()

# ===== Build report =====
report_people = [selected_person] if selected_person else people_all

# Overall compliance
all_recs_for_calc = [
    {"expiry_date": date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None}
    for r in records_all if any(p["id"] == r["person_id"] for p in report_people)
]
overall = compliance_summary(all_recs_for_calc, today=today) if all_recs_for_calc else {"score": 100, "expired": 0, "week": 0, "total": 0}

_BG = {"expired": "#FECACA", "7": "#FECACA", "30": "#FEF3C7", "90": "#FEF9C3", None: "#DCFCE7"}
_FG = {"expired": "#991B1B", "7": "#991B1B", "30": "#92400E", "90": "#713F12", None: "#166534"}
score_col = "#16A34A" if overall["score"] >= 90 else "#D97706" if overall["score"] >= 60 else "#DC2626"

# Category group headers
cat_groups: dict[str, list] = {}
for t in sorted_types:
    cat_groups.setdefault(t.get("category") or "General", []).append(t)

cat_row = '<th rowspan="2" style="background:#1E293B;color:white;padding:10px 14px;min-width:160px;text-align:left;border:1px solid #334155;vertical-align:middle;">Person</th>'
if include_scores:
    cat_row += '<th rowspan="2" style="background:#1E293B;color:white;padding:10px 8px;width:56px;text-align:center;border:1px solid #334155;vertical-align:middle;">Score</th>'
for cat, cat_types in cat_groups.items():
    cat_row += f'<th colspan="{len(cat_types)}" style="background:#334155;color:#CBD5E1;font-size:0.66em;letter-spacing:0.1em;text-transform:uppercase;padding:5px 8px;text-align:center;border:1px solid #475569;">{cat}</th>'

type_row = ""
for t in sorted_types:
    type_row += f'<th style="background:#F8FAFC;color:#475569;font-size:0.66em;letter-spacing:0.04em;text-transform:uppercase;padding:6px 6px;text-align:center;border:1px solid #E2E8F0;white-space:nowrap;writing-mode:vertical-rl;transform:rotate(180deg);height:90px;">{t["name"]}</th>'

# Table rows
tbody = ""
for p in report_people:
    recs_p = [{"expiry_date": date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None} for r in records_all if r["person_id"] == p["id"]]
    ps = compliance_summary(recs_p, today=today) if recs_p else {"score": 100, "expired": 0}
    ps_col = "#16A34A" if ps["score"] >= 90 else "#D97706" if ps["score"] >= 60 else "#DC2626"
    req_ids = req_by_role.get(p.get("job_title") or "", set())

    cells = f'<td style="font-weight:600;padding:8px 12px;border:1px solid #F1F5F9;min-width:160px;">{p["name"]}<br><small style="color:#64748B;font-weight:400;">{p.get("job_title") or "—"}</small></td>'
    if include_scores:
        cells += f'<td style="text-align:center;padding:8px 6px;border:1px solid #F1F5F9;color:{ps_col};font-weight:700;">{ps["score"]}%</td>'

    for t in sorted_types:
        rec = rec_by_pair.get((p["id"], t["id"]))
        if rec and rec.get("expiry_date"):
            exp = date.fromisoformat(rec["expiry_date"]) if isinstance(rec["expiry_date"], str) else rec["expiry_date"]
            w = classify_window(exp, today=today)
            bg, fg = _BG.get(w, "#DCFCE7"), _FG.get(w, "#166534")
            cells += f'<td style="background:{bg};color:{fg};text-align:center;padding:7px 6px;border:1px solid rgba(0,0,0,0.04);white-space:nowrap;">{exp.strftime("%d %b %y")}</td>'
        elif rec and rec.get("completed_date"):
            cells += '<td style="background:#F1F5F9;color:#64748B;text-align:center;padding:7px 6px;border:1px solid rgba(0,0,0,0.04);font-style:italic;">Lifetime</td>'
        elif include_req and t["id"] in req_ids:
            cells += '<td style="background:#FEE2E2;color:#991B1B;text-align:center;padding:7px 6px;border:1px solid rgba(0,0,0,0.04);font-weight:700;font-size:0.7em;letter-spacing:0.04em;text-transform:uppercase;">REQUIRED</td>'
        else:
            cells += '<td style="background:#F8FAFC;color:#CBD5E1;text-align:center;padding:7px 6px;border:1px solid rgba(0,0,0,0.04);">—</td>'
    tbody += f"<tr>{cells}</tr>"

co = f" — {company_name}" if company_name else ""
person_label = selected_person["name"] if selected_person else "Full Workforce"

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Training Compliance Report{co}</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;padding:20px;background:#F8FAFC;color:#0F172A;font-size:12px;}}
  .tip{{background:#FFFBF6;border:1px solid #FFD9B8;border-radius:8px;padding:10px 14px;margin-bottom:16px;color:#92400E;font-size:0.85rem;}}
  .header{{background:linear-gradient(135deg,#0F172A,#1E293B);color:white;border-radius:12px;padding:24px 28px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:flex-start;}}
  .header h1{{margin:0 0 4px 0;font-size:1.35rem;font-weight:700;}}
  .header .sub{{color:#94A3B8;font-size:0.8rem;}}
  .score-big{{font-size:2.2rem;font-weight:800;color:{score_col};line-height:1;}}
  .score-lbl{{color:#94A3B8;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:3px;}}
  .summary{{display:flex;gap:12px;margin-bottom:20px;}}
  .si{{background:white;border:1px solid #E2E8F0;border-radius:8px;padding:12px 16px;flex:1;text-align:center;}}
  .si .sv{{font-size:1.4rem;font-weight:700;}}
  .si .sl{{font-size:0.65rem;color:#64748B;text-transform:uppercase;letter-spacing:0.06em;margin-top:2px;}}
  .wrap{{overflow-x:auto;border-radius:10px;border:1px solid #E2E8F0;background:white;}}
  table{{border-collapse:collapse;width:100%;}}
  tr:hover{{background:rgba(248,250,252,0.6);}}
  .footer{{margin-top:20px;text-align:center;color:#94A3B8;font-size:0.72rem;border-top:1px solid #E2E8F0;padding-top:14px;}}
  @media print{{
    body{{background:white;padding:8px;}}
    .tip,.no-print{{display:none;}}
    .header,.summary .si{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
    .wrap{{overflow:visible;}}
    table{{font-size:10px;}}
  }}
</style></head><body>
<div class="tip no-print"><b>Save as PDF:</b> Ctrl+P (⌘+P on Mac) → Destination: Save as PDF → Landscape orientation recommended for wide matrices.</div>
<div class="header">
  <div>
    <div style="font-size:0.65rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">Training Compliance Audit Report</div>
    <h1>{person_label}{co}</h1>
    <div class="sub">Generated {today.strftime("%d %B %Y")} · {len(report_people)} {'person' if len(report_people)==1 else 'people'} · {len(sorted_types)} training types</div>
  </div>
  <div style="text-align:right;">
    <div class="score-big">{overall["score"]}%</div>
    <div class="score-lbl">Compliance score</div>
  </div>
</div>
<div class="summary">
  <div class="si"><div class="sv">{len(report_people)}</div><div class="sl">People</div></div>
  <div class="si"><div class="sv" style="color:#DC2626;">{overall["expired"]}</div><div class="sl">Expired</div></div>
  <div class="si"><div class="sv" style="color:#D97706;">{overall["week"]}</div><div class="sl">Due ≤7 days</div></div>
  <div class="si"><div class="sv" style="color:{score_col};">{overall["score"]}%</div><div class="sl">Compliance</div></div>
</div>
<div class="wrap">
<table><thead>
  <tr>{cat_row}</tr>
  <tr>{type_row}</tr>
</thead><tbody>{tbody}</tbody></table>
</div>
<div class="footer">Beacon Training Matrix · {today.strftime("%d %B %Y")} · Confidential</div>
</body></html>"""

# Download + preview
fname = f"compliance_{person_label.replace(' ', '_')}_{today.strftime('%Y%m%d')}.html"
st.download_button(
    "Download report (.html → open in browser → Ctrl+P → Save as PDF)",
    data=HTML, file_name=fname, mime="text/html", type="primary",
)
st.markdown("---")
st.caption("Preview (scroll right for full matrix):")
st.components.v1.html(HTML, height=700, scrolling=True)
