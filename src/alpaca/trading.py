"""Account manager for Alpaca API."""

import os

from dotenv import load_dotenv
from common import with_alpaca_trading_client
from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, AssetStatus, OrderSide, QueryOrderStatus
from alpaca.trading.models import Asset, Order, TradeAccount
from alpaca.trading.requests import GetAssetsRequest, GetOrdersRequest

load_dotenv()
#ALPACA_KEY = os.getenv("ALPACA_KEY")
#ALPACA_SECRET = os.getenv("ALPACA_SECRET")

#trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)

@with_alpaca_trading_client
def get_acc_info(trading_client) -> TradeAccount | RawData:
    """Get account info from AlpacaAPI."""
    account = trading_client.get_account()
    return account

@with_alpaca_trading_client
def search_assets(trading_client: TradingClient, asset_class: AssetClass | None = None, status: AssetStatus | None = None) -> list[Asset] | RawData:
    """Search assets from AlpacaAPI."""
    search_params = GetAssetsRequest(asset_class=asset_class, status=status)
    return trading_client.get_all_assets(search_params)

@with_alpaca_trading_client
def get_orders_info(trading_client: TradingClient, status: QueryOrderStatus = QueryOrderStatus.ALL, side: OrderSide | None = None) -> list[Order] | RawData:
    """Get orders info from AlpacaAPI."""
    request_params = GetOrdersRequest(status=status, side=side)
    return trading_client.get_orders(filter=request_params)

#print(get_acc_info())
#print(search_assets())
#print(get_orders_info())