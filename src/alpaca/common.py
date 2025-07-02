"""Decorator for logging in."""

import os

from dotenv import load_dotenv

from alpaca.trading.client import TradingClient


def with_alpaca_trading_client(func):
    """Provides Alpaca TradingClient authentication decorator."""

    def wrapper(*args, **kwargs):
        load_dotenv()
        alpaca_key = os.getenv("ALPACA_KEY")
        alpaca_secret = os.getenv("ALPACA_SECRET")
        client = TradingClient(alpaca_key, alpaca_secret, paper=True)
        return func(client, *args, **kwargs)

    return wrapper
