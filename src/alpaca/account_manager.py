"""Account manager for Alpaca API."""

import os

from dotenv import load_dotenv

from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, AssetStatus, OrderSide, QueryOrderStatus
from alpaca.trading.models import Asset, Order, TradeAccount
from alpaca.trading.requests import GetAssetsRequest, GetOrdersRequest

load_dotenv()
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)

def get_acc_info(trading_client) -> TradeAccount | RawData:
    """Get account info from AlpacaAPI."""
    account = trading_client.get_account()
    print(account)
    return account

print(get_acc_info())
def search_assets(asset_class: AssetClass | None = None, status: AssetStatus | None = None) -> list[Asset] | RawData:
    """Search assets from AlpacaAPI."""
    search_params = GetAssetsRequest(asset_class=asset_class, status=status)
    return trading_client.get_all_assets(search_params)


def get_orders_info(status: QueryOrderStatus, side: OrderSide) -> list[Order] | RawData:
    """Get orders info from AlpacaAPI."""
    request_params = GetOrdersRequest(status=status, side=side)
    return trading_client.get_orders(filter=request_params)
