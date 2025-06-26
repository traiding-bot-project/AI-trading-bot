import os
from typing import Optional

from dotenv import load_dotenv
from alpaca.trading.enums import OrderSide, QueryOrderStatus, TimeInForce
from alpaca.trading.models import Order
from alpaca.trading.requests import GetOrdersRequest
from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest


load_dotenv()
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")


trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)

def get_orders_info(status: QueryOrderStatus, side: OrderSide) -> list[Order] | RawData:
    """Get orders info from AlpacaAPI."""
    request_params = GetOrdersRequest(status=status, side=side)
    return trading_client.get_orders(filter=request_params)


def prepare_order(symbol: str,
                  side, 
                  asset_qty: Optional[float],
                  asset_in_money: Optional[float], 
                  time_in_force = TimeInForce.DAY
                  ) -> :
    market_order_request = MarketOrderRequest(
        symbol = symbol,
        qty = 
        notional = 
    )