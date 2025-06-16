import os

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass, AssetStatus
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, QueryOrderStatus
from dotenv import load_dotenv

load_dotenv()
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)


def get_acc_info():
    account = trading_client.get_account()
    return account


def search_assets(asset_class: AssetClass = None, status: AssetStatus = None):
    search_params = GetAssetsRequest(asset_class=asset_class, status=status)
    return trading_client.get_all_assets(search_params)


def get_orders_info(status: QueryOrderStatus, side: OrderSide):
    request_params = GetOrdersRequest(status=status, side=side)
    return trading_client.get_orders(filter=request_params)
