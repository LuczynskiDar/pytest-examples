from unittest.mock import patch

import pytest
from src.shop.notifications import EmailNotifier


@pytest.mark.parametrize(
    ("test_recipient", "test_subject", "test_body"),
    [
        (
            "test_customer@example.com",
            "Hello this is a test",
            "We're making a send message unit test",
        )
    ],
)
def test_email_notifier_send(
    correct_email_notifier: EmailNotifier, test_recipient: str, test_subject: str, test_body: str
) -> None:
    with patch("src.shop.notifications.smtplib.SMTP") as magic_mock:
        correct_email_notifier.send(test_recipient, test_subject, test_body)
    server = magic_mock.return_value.__enter__.return_value
    message = server.send_message.call_args.args[0]
    assert message["To"] == test_recipient
    assert message["Subject"] == test_subject
    assert message.get_content().strip() == test_body
    magic_mock.assert_called_once_with(correct_email_notifier.host, correct_email_notifier.port)
