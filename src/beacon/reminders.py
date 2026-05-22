"""Reminder logic: classify expiry windows, find due items, build digest emails."""

from datetime import date
from typing import Optional


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
