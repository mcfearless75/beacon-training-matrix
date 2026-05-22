from datetime import date

import pandas as pd
import streamlit as st

from app.auth import require_auth
from app.branding import inject_css, page_header
from beacon.db import anon_client
from beacon.reminders import classify_window

require_auth()
inject_css()
page_header("Training Matrix", "Every person, every training type — coloured by time-to-expiry.")

sb = anon_client()
people = sb.table("people").select("id, name").eq("active", True).order("name").execute().data
types = sb.table("training_types").select("id, name").eq("active", True).order("name").execute().data
records = sb.table("training_records").select("person_id, training_type_id, expiry_date, completed_date, notes").execute().data

rec_by_pair = {(r["person_id"], r["training_type_id"]): r for r in records}


def colour(window):
    return {
        "expired": "#e57373",
        "7": "#e57373",
        "30": "#ffb74d",
        "90": "#fff176",
        None: "#a5d6a7",
    }.get(window, "#e0e0e0")


columns = ["Person"] + [t["name"] for t in types]
data = []
styles = []
for p in people:
    row = {"Person": p["name"]}
    row_styles = {"Person": ""}
    for t in types:
        rec = rec_by_pair.get((p["id"], t["id"]))
        if rec and rec["expiry_date"]:
            exp = date.fromisoformat(rec["expiry_date"])
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

df = pd.DataFrame(data, columns=columns)


def styler(_):
    return pd.DataFrame(styles, columns=columns)


st.dataframe(df.style.apply(styler, axis=None), use_container_width=True)

st.divider()
st.subheader("Edit a record")
if people and types:
    person = st.selectbox("Person", options=people, format_func=lambda p: p["name"])
    ttype = st.selectbox("Training type", options=types, format_func=lambda t: t["name"])
    existing = rec_by_pair.get((person["id"], ttype["id"]))
    completed = st.date_input(
        "Completed date",
        value=date.fromisoformat(existing["completed_date"]) if existing and existing.get("completed_date") else None,
    )
    expiry = st.date_input(
        "Expiry date (leave blank for lifetime)",
        value=date.fromisoformat(existing["expiry_date"]) if existing and existing.get("expiry_date") else None,
    )
    notes = st.text_input("Notes", value=(existing or {}).get("notes") or "")
    if st.button("Save"):
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
else:
    st.info("Add people and training types first.")
