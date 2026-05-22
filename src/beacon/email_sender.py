"""Thin wrapper over the Resend SDK for sending transactional emails."""

import resend


def send_email(*, api_key: str, sender: str, to: str, subject: str, html: str) -> str:
    """Send an HTML email via Resend. Returns the provider message id."""
    resend.api_key = api_key
    response = resend.Emails.send({
        "from": sender,
        "to": [to],
        "subject": subject,
        "html": html,
    })
    return response["id"]
