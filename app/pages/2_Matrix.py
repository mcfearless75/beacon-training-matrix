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
    "Each cell shows when training expires. Colour shows urgency. "
    "<b>Required — Missing</b> (red, bold) means that training is mandatory for that person's role but has no record. "
    "Use filters to narrow the view. Edit a record below to add or update one entry.",
)
colour_legend()

sb = anon_client()
people = sb.table("people").select("id, name, job_title").eq("active", True).order("name").execute().data
types_raw = sb.table("training_types").select("id, name, category").eq("active", True).order("name").execute().data
records = (
    sb.table("training_records")
    .select("person_id, training_type_id, expiry_date, completed_date, notes")
    .execute()
    .data
)
requirements_raw = sb.table("role_requirements").select("job_title, training_type_id").execute().data

rec_by_pair = {(r["person_id"], r["training_type_id"]): r for r in records}
req_by_role: dict[str, set] = {}
for r in requirements_raw:
    req_by_role.setdefault(r["job_title"], set()).add(r["training_type_id"])

# ===== Filter bar =====
f1, f2, f3 = st.columns([2, 1, 2])
with f1:
    search = st.text_input(
        "Search", placeholder="Filter by name or job title…", label_visibility="collapsed",
    ).strip().lower()
with f2:
    status_filter = st.selectbox(
        "Status",
        options=["All statuses", "Required — missing", "Needs attention (≤90 days)", "Expired only", "≤30 days", "In date only"],
        label_visibility="collapsed",
    )
with f3:
    type_filter = st.multiselect(
        "Training types", options=[t["name"] for t in types_raw],
        placeholder="All training types", label_visibility="collapsed",
    )

_CELL_BG = {"expired": "#FEE2E2", "7": "#FEE2E2", "30": "#FEF3C7", "90": "#FEF9C3", None: "#DCFCE7"}
_CELL_FG = {"expired": "#991B1B", "7": "#991B1B", "30": "#92400E", "90": "#713F12", None: "#166534"}


def row_passes_filter(p, person_recs):
    if search and search not in f"{p['name']} {p.get('job_title') or ''}".lower():
        return False
    if status_filter == "All statuses":
        return True
    if status_filter == "Required — missing":
        req_ids = req_by_role.get(p.get("job_title") or "", set())
        if not req_ids:
            return False
        return any(not rec_by_pair.get((p["id"], tid)) for tid in req_ids)
    today = date.today()
    for rec in person_recs:
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
    return status_filter == "In date only" and not [r for r in person_recs if r]


# Sort visible types by category then name for grouping
visible_types = sorted(
    [t for t in types_raw if not type_filter or t["name"] in type_filter],
    key=lambda t: (t.get("category") or "General", t["name"]),
)

today = date.today()
rows_data = []
for p in people:
    person_recs = [rec_by_pair.get((p["id"], t["id"])) for t in visible_types]
    if not row_passes_filter(p, person_recs):
        continue
    row: dict = {"_pid": p["id"], "_job": p.get("job_title") or "", "Person": p["name"]}
    required_ids = req_by_role.get(p.get("job_title") or "", set())
    for t in visible_types:
        rec = rec_by_pair.get((p["id"], t["id"]))
        if rec and rec.get("expiry_date"):
            exp = date.fromisoformat(rec["expiry_date"]) if isinstance(rec["expiry_date"], str) else rec["expiry_date"]
            window = classify_window(exp, today=today)
            row[t["name"]] = {"display": exp.strftime("%d %b %y"), "window": window, "kind": "dated"}
        elif rec and rec.get("completed_date"):
            row[t["name"]] = {"display": "Lifetime", "window": None, "kind": "lifetime"}
        elif t["id"] in required_ids:
            row[t["name"]] = {"display": "Required", "window": "expired", "kind": "required-missing"}
        else:
            row[t["name"]] = {"display": "", "window": None, "kind": "missing"}
    rows_data.append(row)


if not rows_data and (search or status_filter != "All statuses" or type_filter):
    st.info("No rows match your filters. Try clearing the search or status filter.")
elif not people:
    st.info("Add people on the People page first.")
elif not types_raw:
    st.info("Add training types on the Training Types page first.")
else:
    # ===== Stats band =====
    total_cells = len(rows_data) * len(visible_types)
    filled = sum(1 for row in rows_data for t in visible_types if row[t["name"]]["kind"] in ("dated", "lifetime"))
    req_missing = sum(1 for row in rows_data for t in visible_types if row[t["name"]]["kind"] == "required-missing")
    expired_n = sum(1 for row in rows_data for t in visible_types if row[t["name"]]["window"] in ("expired", "7"))
    coverage = round(100 * filled / total_cells) if total_cells else 100
    cov_col = "#16A34A" if coverage >= 80 else "#D97706" if coverage >= 60 else "#DC2626"
    exp_col = "#DC2626" if expired_n > 0 else "#16A34A"
    req_col = "#DC2626" if req_missing > 0 else "#94A3B8"

    st.markdown(
        '<div class="matrix-stats">'
        f'<div class="mstat"><div class="mstat-label">People</div><b>{len(rows_data)}</b></div>'
        f'<div class="mstat"><div class="mstat-label">Types</div><b>{len(visible_types)}</b></div>'
        f'<div class="mstat"><div class="mstat-label">Coverage</div><b style="color:{cov_col};">{coverage}%</b></div>'
        f'<div class="mstat"><div class="mstat-label">Expired / Due</div><b style="color:{exp_col};">{expired_n}</b></div>'
        f'<div class="mstat"><div class="mstat-label">Req. Missing</div><b style="color:{req_col};">{req_missing}</b></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ===== Category group headers =====
    cat_groups: dict[str, list] = {}
    for t in visible_types:
        cat = t.get("category") or "General"
        cat_groups.setdefault(cat, []).append(t)

    cat_row = '<th class="mat-th mat-th-person" rowspan="2">Person</th>'
    for cat, cat_types in cat_groups.items():
        cat_row += f'<th class="mat-th mat-cat-header" colspan="{len(cat_types)}">{cat}</th>'

    type_row = "".join(f'<th class="mat-th">{t["name"]}</th>' for t in visible_types)
    thead = f'<tr>{cat_row}</tr><tr>{type_row}</tr>'

    # ===== Table rows =====
    tbody = ""
    for row in rows_data:
        cells = f'<td class="mat-td mat-td-person">{row["Person"]}<br><small style="color:#94A3B8;font-weight:400;">{row["_job"]}</small></td>'
        for t in visible_types:
            cell = row[t["name"]]
            if cell["kind"] == "required-missing":
                cells += '<td class="mat-td mat-required">Required</td>'
            elif cell["kind"] == "missing":
                cells += '<td class="mat-td mat-missing">—</td>'
            elif cell["kind"] == "lifetime":
                cells += '<td class="mat-td mat-lifetime">Lifetime</td>'
            else:
                bg = _CELL_BG.get(cell["window"], "#DCFCE7")
                fg = _CELL_FG.get(cell["window"], "#166534")
                cells += f'<td class="mat-td" style="background:{bg};color:{fg};">{cell["display"]}</td>'
        tbody += f"<tr>{cells}</tr>"

    st.markdown(
        '<div class="matrix-wrap"><table class="matrix-table"><thead>'
        + thead + '</thead><tbody>' + tbody + '</tbody></table></div>',
        unsafe_allow_html=True,
    )

    # CSV export
    export_rows = [{"Person": row["Person"], **{t["name"]: row[t["name"]]["display"] for t in visible_types}} for row in rows_data]
    st.download_button(
        "Export current view as CSV",
        data=pd.DataFrame(export_rows).to_csv(index=False),
        file_name="training_matrix.csv",
        mime="text/csv",
    )

st.divider()

# ===== Edit / Bulk tabs =====
edit_tab, bulk_tab = st.tabs(["✎ Edit a record", "⚡ Bulk update"])

with edit_tab:
    if not people or not types_raw:
        st.info("Add people and training types first.")
    else:
        person = st.selectbox("Person", options=people, format_func=lambda p: p["name"], key="edit_person")
        ttype = st.selectbox("Training type", options=types_raw, format_func=lambda t: t["name"], key="edit_type")
        existing = rec_by_pair.get((person["id"], ttype["id"]))
        c1, c2 = st.columns(2)
        with c1:
            completed = st.date_input(
                "Completed date",
                value=date.fromisoformat(existing["completed_date"]) if existing and existing.get("completed_date") else None,
                key="edit_completed",
            )
        with c2:
            expiry = st.date_input(
                "Expiry date (blank = lifetime)",
                value=date.fromisoformat(existing["expiry_date"]) if existing and existing.get("expiry_date") else None,
                key="edit_expiry",
            )
        notes = st.text_input("Notes", value=(existing or {}).get("notes") or "", key="edit_notes")
        if existing:
            w = classify_window(date.fromisoformat(existing["expiry_date"]), today=today) if existing.get("expiry_date") else None
            status_label = {"expired": "Expired", "7": "≤ 7 days", "30": "≤ 30 days", "90": "≤ 90 days"}.get(w, "In date") if existing.get("expiry_date") else "Lifetime"
            st.caption(f"Current status: **{status_label}**")
        if st.button("Save record", key="edit_save", type="primary"):
            sb.table("training_records").upsert(
                {"person_id": person["id"], "training_type_id": ttype["id"],
                 "completed_date": completed.isoformat() if completed else None,
                 "expiry_date": expiry.isoformat() if expiry else None,
                 "notes": notes or None},
                on_conflict="person_id,training_type_id",
            ).execute()
            st.success(f"Saved — {person['name']} / {ttype['name']}.")
            st.rerun()

with bulk_tab:
    st.caption("Mark **multiple people** complete on the **same training type** at once. Ideal after a group training day.")
    if not people or not types_raw:
        st.info("Add people and training types first.")
    else:
        bulk_type = st.selectbox("Training type", options=types_raw, format_func=lambda t: t["name"], key="bulk_type")
        bulk_people = st.multiselect(
            "People to update", options=people, format_func=lambda p: p["name"],
            placeholder="Select people…", key="bulk_people",
        )
        b1, b2 = st.columns(2)
        with b1:
            bulk_completed = st.date_input("Completed on", value=date.today(), key="bulk_completed")
        with b2:
            bulk_expiry = st.date_input("Expires on (blank = lifetime)", value=None, key="bulk_expiry")
        bulk_notes = st.text_input("Notes (applied to all)", key="bulk_notes")
        if st.button(
            f"Mark {len(bulk_people)} {'person' if len(bulk_people)==1 else 'people'} complete",
            disabled=not bulk_people, key="bulk_save", type="primary",
        ):
            sb.table("training_records").upsert(
                [{"person_id": p["id"], "training_type_id": bulk_type["id"],
                  "completed_date": bulk_completed.isoformat() if bulk_completed else None,
                  "expiry_date": bulk_expiry.isoformat() if bulk_expiry else None,
                  "notes": bulk_notes or None} for p in bulk_people],
                on_conflict="person_id,training_type_id",
            ).execute()
            st.success(f"Updated {len(bulk_people)} records for {bulk_type['name']}.")
            st.rerun()
