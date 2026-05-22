"""Daily reminder job. Run via `python -m cron.run_reminders`."""
from datetime import date
from beacon.db import service_client
from beacon.email_sender import send_email
from beacon.reminders import find_due_items, build_digest
from beacon.config import load_config


def fetch_records(sb):
    """Active records with expiry, joined with person + type names."""
    records = sb.rpc("get_active_training_records").execute().data or []
    return [
        {
            "id": r["id"],
            "expiry_date": date.fromisoformat(r["expiry_date"]) if r["expiry_date"] else None,
            "person_name": r["person_name"],
            "training_name": r["training_name"],
        }
        for r in records
    ]


def fetch_already_sent(sb, today: date) -> set[tuple[str, str]]:
    rows = (
        sb.table("reminder_log")
        .select("training_record_id, window")
        .eq("status", "sent")
        .gte("sent_at", today.isoformat())
        .execute()
        .data
        or []
    )
    return {(r["training_record_id"], r["window"]) for r in rows}


def fetch_settings(sb) -> dict:
    return sb.table("settings").select("*").eq("id", 1).single().execute().data


def log_send(sb, item, recipient, status, msg_id=None, error=None):
    sb.table("reminder_log").upsert(
        {
            "training_record_id": item["id"],
            "window": item["window"],
            "recipient_email": recipient,
            "status": status,
            "error": (error[:500] if error else None),
        },
        on_conflict="training_record_id,window",
    ).execute()


def run() -> dict:
    cfg = load_config()
    sb = service_client()
    settings = fetch_settings(sb)
    recipient = settings.get("reminder_recipient_email")
    if not recipient:
        print("[reminders] No recipient configured. Skipping.")
        return {"sent_count": 0, "skipped": "no_recipient"}

    today = date.today()
    records = fetch_records(sb)
    already_sent = fetch_already_sent(sb, today=today)
    due = find_due_items(records, already_sent=already_sent, today=today)

    digest = build_digest(due, app_url=cfg.app_base_url)
    if digest is None:
        print("[reminders] Nothing due today.")
        return {"sent_count": 0}

    subject, html = digest
    sender = f"{settings.get('sender_name','Beacon')} <{settings.get('sender_email', cfg.sender_email)}>"

    try:
        msg_id = send_email(
            api_key=cfg.resend_api_key,
            sender=sender, to=recipient,
            subject=subject, html=html,
        )
        for item in due:
            log_send(sb, item, recipient, "sent", msg_id=msg_id)
        print(f"[reminders] Sent {len(due)} items, message {msg_id}")
        return {"sent_count": len(due), "message_id": msg_id}
    except Exception as e:
        for item in due:
            log_send(sb, item, recipient, "failed", error=str(e))
        raise


if __name__ == "__main__":
    run()
