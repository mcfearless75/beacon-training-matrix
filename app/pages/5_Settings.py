import tempfile

import streamlit as st

from app.auth import require_admin
from beacon.db import anon_client, service_client
from beacon.importer import parse_matrix_workbook

require_admin()
st.title("Settings")
sb = anon_client()

settings = sb.table("settings").select("*").eq("id", 1).single().execute().data or {}
st.subheader("Reminder recipient")
recipient = st.text_input("Recipient email", value=settings.get("reminder_recipient_email") or "")
sender_email = st.text_input("Sender email (must be verified in Resend)", value=settings.get("sender_email") or "")
sender_name = st.text_input("Sender name", value=settings.get("sender_name") or "Beacon Training Matrix")
if st.button("Save settings"):
    sb.table("settings").update({
        "reminder_recipient_email": recipient or None,
        "sender_email": sender_email or None,
        "sender_name": sender_name or None,
    }).eq("id", 1).execute()
    st.success("Saved.")

st.divider()
st.subheader("Import from xlsx")
uploaded = st.file_uploader("Training Matrix.xlsx", type=["xlsx"])
header_row = st.number_input("Header row (1-indexed)", value=7)
name_col = st.text_input("Name column letter", value="A")
job_col = st.text_input("Job title column letter", value="D")
start_col = st.text_input("Start date column letter", value="I")
training_start_col = st.text_input("First training-type column letter", value="J")

if uploaded and st.button("Import"):
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name
    parsed = parse_matrix_workbook(
        tmp_path,
        header_row=int(header_row),
        name_col=name_col,
        job_col=job_col,
        start_col=start_col,
        training_start_col=training_start_col,
    )
    svc = service_client()
    for tname in parsed["training_types"]:
        svc.table("training_types").upsert({"name": tname}, on_conflict="name").execute()
    for p in parsed["people"]:
        svc.table("people").upsert(p, on_conflict="name").execute()
    st.success(
        f"Imported {len(parsed['people'])} people and {len(parsed['training_types'])} training types."
    )
