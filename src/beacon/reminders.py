"""Reminder logic: classify expiry windows, find due items, build digest emails."""

from collections import defaultdict
from datetime import date
from typing import Iterable, Optional, Set, Tuple


WINDOW_LABELS = [
    ("expired", "Expired / overdue"),
    ("7", "Expiring within 7 days"),
    ("30", "Expiring within 30 days"),
    ("90", "Expiring within 90 days"),
]


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


def build_digest(items: list[dict], app_url: str) -> Optional[Tuple[str, str]]:
    """Build a daily digest email from due items, grouped by reminder window.

    Returns (subject, html) or None when there are no items.
    """
    if not items:
        return None
    groups: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        groups[it["window"]].append(it)

    subject = f"Beacon Training Matrix - {len(items)} items expiring"

    sections = []
    for key, label in WINDOW_LABELS:
        rows = groups.get(key, [])
        if not rows:
            continue
        rows_html = "".join(
            f"<li><b>{r['person_name']}</b> - {r['training_name']} - expires "
            f"{r['expiry_date'].strftime('%d %b %Y')}</li>"
            for r in rows
        )
        sections.append(f"<h3>{label} ({len(rows)})</h3><ul>{rows_html}</ul>")

    html = (
        "<p>Daily training expiry digest from the Beacon Training Matrix.</p>"
        f"{''.join(sections)}"
        f"<p><a href='{app_url}'>Open the matrix -></a></p>"
    )
    return subject, html
