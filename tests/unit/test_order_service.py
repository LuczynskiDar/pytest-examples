from unittest.mock import MagicMock

from src.shop.order import Order
from src.shop.order_service import OrderService


def test_checkout(
    mock_gateway: MagicMock, mock_notification: MagicMock, correct_order: Order
) -> None:
    service = OrderService(mock_gateway, mock_notification)
    _ = service.checkout(correct_order)
    mock_gateway.charge.assert_called_once()
    mock_notification.send_order_confirmation.assert_called_once()
