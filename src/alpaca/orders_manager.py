import os

from dotenv import load_dotenv
from alpaca.trading.enums import OrderSide, QueryOrderStatus
from alpaca.trading.models import Order
from alpaca.trading.requests import GetOrdersRequest

trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)

def get_orders_info(status: QueryOrderStatus, side: OrderSide) -> list[Order] | RawData:
    """Get orders info from AlpacaAPI."""
    request_params = GetOrdersRequest(status=status, side=side)
    return trading_client.get_orders(filter=request_params)