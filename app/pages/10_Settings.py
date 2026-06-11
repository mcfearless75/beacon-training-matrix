import tempfile

import streamlit as st

from app.auth import require_admin
from app.branding import help_box, inject_css, page_header, page_tour
from beacon.db import anon_client, service_client
from beacon.importer import parse_matrix_workbook

require_admin()
inject_css()
page_header("Settings", "Reminder recipient, sender details, and bulk import.")
page_tour(
    "settings",
    "Two jobs live here: reminder emails and importing your old spreadsheet.",
    [
        ("Reminder email",
         "Choose who gets the daily email about training that's about to run out."),
        ("Import a spreadsheet",
         "Already track training in Excel? Upload the file and the app fills itself in — "
         "no retyping."),
    ],
)
help_box(
    "Two things to configure",
    "<b>Reminder email</b> — who gets the daily expiry digest, and which address it's sent from. "
    "<b>Import</b> — if you have an existing training matrix spreadsheet, upload it here to "
    "bulk-load people and training types in one go.",
)
sb = service_client()  # admin page — service role bypasses RLS; gated by require_admin()

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
c1, c2 = st.columns(2)
with c1:
    name_col = st.text_input("Name column letter", value="A")
    job_col = st.text_input("Job title column letter", value="D")
    start_col = st.text_input("Start date column letter", value="I")
with c2:
    email_col = st.text_input("Email column letter (optional)", value="",
                              help="Leave blank if your spreadsheet has no email column.")
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
        email_col=email_col.strip() or None,
    )
    svc = service_client()
    for tname in parsed["training_types"]:
        svc.table("training_types").upsert({"name": tname}, on_conflict="name").execute()
    for p in parsed["people"]:
        svc.table("people").upsert(p, on_conflict="name").execute()
    st.success(
        f"Imported {len(parsed['people'])} people and {len(parsed['training_types'])} training types."
    )
