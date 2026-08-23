"""Pure validation logic for the certificate approval flow."""

from datetime import date


def validate_approval(expiry_date: date | None, is_lifetime: bool) -> str | None:
    """Check whether a certificate approval has enough info to proceed.

    Returns an error message if invalid, or None if the approval can go ahead.
    """
    if not is_lifetime and expiry_date is None:
        return "Set an expiry date, or tick 'No expiry' for a lifetime cert."
    return None


def is_expiry_in_past(expiry_date: date | None, today: date) -> bool:
    """True if the given expiry date already lies in the past relative to today."""
    if expiry_date is None:
        return False
    return expiry_date < today
