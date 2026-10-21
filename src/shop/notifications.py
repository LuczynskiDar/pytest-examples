import smtplib
from email.message import EmailMessage

from src.shop.order import Order


class EmailNotifier:
    """Send e-mails through an SMTP server."""

    def __init__(self, host: str, port: int = 25, sender: str = "shop@example.com") -> None:
        self.host = host
        self.port = port
        self.sender = sender

    def send(self, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port) as server:
            server.send_message(message)

    def send_order_confirmation(self, order: Order) -> None:
        self.send(
            recipient=order.customer.email,
            subject="Order confirmation",
            body=f"Hello {order.customer.name}, your order total is {order.total():.2f}.",
        )
