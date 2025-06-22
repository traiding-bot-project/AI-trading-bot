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


def get_acc_info() -> TradeAccount | RawData:
    """Get account info from AlpacaAPI."""
    account = trading_client.get_account()
    if account.trading_blocked:
        return {"message": "trading blocked"}
    else:
        return {"balance": account.buying_power, "acc_info": account}


def get_balance_change():
    account = trading_client.get_account()
    balance_change = float(account.equity) - float(account.last_equity)
    return balance_change

