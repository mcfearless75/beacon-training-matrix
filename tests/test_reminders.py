from datetime import date

from beacon.reminders import classify_window


def test_classify_window_expired_today():
    assert classify_window(date(2026, 5, 22), today=date(2026, 5, 22)) == "expired"


def test_classify_window_expired_past():
    assert classify_window(date(2026, 5, 1), today=date(2026, 5, 22)) == "expired"


def test_classify_window_7_day():
    assert classify_window(date(2026, 5, 29), today=date(2026, 5, 22)) == "7"


def test_classify_window_30_day():
    assert classify_window(date(2026, 6, 15), today=date(2026, 5, 22)) == "30"


def test_classify_window_90_day():
    assert classify_window(date(2026, 7, 30), today=date(2026, 5, 22)) == "90"


def test_classify_window_outside_returns_none():
    assert classify_window(date(2027, 1, 1), today=date(2026, 5, 22)) is None


def test_classify_window_boundary_7():
    assert classify_window(date(2026, 5, 29), today=date(2026, 5, 22)) == "7"


def test_classify_window_boundary_8():
    assert classify_window(date(2026, 5, 30), today=date(2026, 5, 22)) == "30"
