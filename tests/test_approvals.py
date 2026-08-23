from datetime import date

from beacon.approvals import is_expiry_in_past, validate_approval


def test_validate_approval_blocks_when_no_date_and_not_lifetime():
    assert validate_approval(None, is_lifetime=False) == (
        "Set an expiry date, or tick 'No expiry' for a lifetime cert."
    )


def test_validate_approval_allows_date_set():
    assert validate_approval(date(2027, 3, 14), is_lifetime=False) is None


def test_validate_approval_allows_lifetime_with_no_date():
    assert validate_approval(None, is_lifetime=True) is None


def test_validate_approval_allows_lifetime_even_if_date_still_set():
    # Lifetime checkbox wins even if a stale date is still sitting in the input.
    assert validate_approval(date(2027, 3, 14), is_lifetime=True) is None


def test_is_expiry_in_past_true_for_past_date():
    assert is_expiry_in_past(date(2026, 1, 1), today=date(2026, 8, 23)) is True


def test_is_expiry_in_past_false_for_future_date():
    assert is_expiry_in_past(date(2027, 1, 1), today=date(2026, 8, 23)) is False


def test_is_expiry_in_past_false_for_today():
    assert is_expiry_in_past(date(2026, 8, 23), today=date(2026, 8, 23)) is False


def test_is_expiry_in_past_false_when_none():
    assert is_expiry_in_past(None, today=date(2026, 8, 23)) is False
