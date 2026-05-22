from unittest.mock import patch

from beacon.email_sender import send_email


@patch("beacon.email_sender.resend")
def test_send_email_calls_resend_with_payload(mock_resend):
    mock_resend.Emails.send.return_value = {"id": "msg_123"}
    msg_id = send_email(
        api_key="re_test",
        sender="Beacon <noreply@beacon.test>",
        to="paulmc18@gmail.com",
        subject="Test",
        html="<p>hi</p>",
    )
    assert msg_id == "msg_123"
    mock_resend.Emails.send.assert_called_once()
    payload = mock_resend.Emails.send.call_args[0][0]
    assert payload["to"] == ["paulmc18@gmail.com"]
    assert payload["subject"] == "Test"
