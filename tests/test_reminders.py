from datetime import date

from beacon.reminders import build_digest, classify_window, find_due_items


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


def test_find_due_items_filters_by_window():
    today = date(2026, 5, 22)
    records = [
        {"id": "r1", "expiry_date": date(2026, 5, 29), "person_name": "A", "training_name": "First Aid"},
        {"id": "r2", "expiry_date": date(2027, 1, 1), "person_name": "B", "training_name": "CSCS"},
        {"id": "r3", "expiry_date": date(2026, 5, 1), "person_name": "C", "training_name": "Induction"},
    ]
    already_sent = {("r1", "7")}
    due = find_due_items(records, already_sent=already_sent, today=today)
    ids = [(d["id"], d["window"]) for d in due]
    assert ("r1", "7") not in ids
    assert ("r3", "expired") in ids
    assert all(i[0] != "r2" for i in ids)


def test_build_digest_groups_by_window_and_skips_empty():
    items = [
        {"id": "r1", "window": "7", "person_name": "Alice", "training_name": "First Aid", "expiry_date": date(2026, 5, 29)},
        {"id": "r2", "window": "expired", "person_name": "Bob", "training_name": "CSCS", "expiry_date": date(2026, 5, 1)},
        {"id": "r3", "window": "30", "person_name": "Carol", "training_name": "Manual Handling", "expiry_date": date(2026, 6, 15)},
    ]
    result = build_digest(items, app_url="http://localhost:8501")
    assert result is not None
    subject, html = result
    assert "3 items" in subject
    assert "Expired" in html
    assert "Bob" in html
    assert "Alice" in html
    assert "First Aid" in html
    assert "29 May 2026" in html
    assert "90 days" not in html


def test_build_digest_empty_returns_none():
    assert build_digest([], app_url="x") is None
