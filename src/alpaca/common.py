"""Decorator for logging in"""

import os

from dotenv import load_dotenv

from alpaca.trading.client import TradingClient


def with_alpaca_trading_client(func):
    def wrapper(*args, **kwargs):
        load_dotenv()
        ALPACA_KEY = os.getenv("ALPACA_KEY")
        ALPACA_SECRET = os.getenv("ALPACA_SECRET")
        client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)
        return func(client, *args, **kwargs)

    return wrapper
