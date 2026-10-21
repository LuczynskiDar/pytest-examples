import logging
import smtplib

from src.shop.notifications import EmailNotifier
from src.shop.order import Order
from src.shop.payment import PaymentGateway

logger = logging.getLogger(__name__)


class OrderService:
    """Checkout flow: charge the customer, mark the order as paid, send a confirmation."""

    def __init__(self, gateway: PaymentGateway, notifier: EmailNotifier) -> None:
        self.gateway = gateway
        self.notifier = notifier

    def checkout(self, order: Order) -> str:
        """Pay for the order and return the transaction id.

        The customer is charged only for orders with status 'new'. A payment failure leaves
        the order untouched. A failure to send the confirmation e-mail is logged and does
        not fail the checkout.
        """
        if order.status != "new":
            raise ValueError(f"Cannot check out an order with status '{order.status}'")

        transaction_id = self.gateway.charge(order.total(), order.customer.email)
        order.pay()

        try:
            self.notifier.send_order_confirmation(order)
        except smtplib.SMTPException:
            logger.warning("Could not send confirmation to %s", order.customer.email)
        return transaction_id
