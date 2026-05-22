"""Reminder logic: classify expiry windows, find due items, build digest emails."""

from datetime import date
from typing import Iterable, Optional, Set, Tuple


def classify_window(expiry: date, today: date) -> Optional[str]:
    """Return the reminder window ("expired", "7", "30", "90") or None."""
    if expiry <= today:
        return "expired"
    delta = (expiry - today).days
    if delta <= 7:
        return "7"
    if delta <= 30:
        return "30"
    if delta <= 90:
        return "90"
    return None


def find_due_items(
    records: Iterable[dict],
    already_sent: Set[Tuple[str, str]],
    today: date,
) -> list[dict]:
    """Return records that fall into a reminder window and haven't been sent.

    `already_sent` is a set of (record_id, window) tuples representing reminders
    already dispatched today — used to dedupe re-runs of the cron job.
    """
    out: list[dict] = []
    for r in records:
        if r.get("expiry_date") is None:
            continue
        window = classify_window(r["expiry_date"], today=today)
        if window is None:
            continue
        if (r["id"], window) in already_sent:
            continue
        out.append({**r, "window": window})
    return out
