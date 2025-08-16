"""Decorator for logging in."""

import os
from collections.abc import Callable
from typing import Concatenate

from dotenv import load_dotenv

from alpaca.trading.client import TradingClient


def with_alpaca_trading_client[P, R](func: Callable[Concatenate[TradingClient, ...], R]) -> Callable[..., R]:
    """Provides Alpaca TradingClient authentication decorator."""

    def wrapper(*args: P, **kwargs: P) -> R:
        load_dotenv()
        alpaca_key = os.getenv("ALPACA_KEY")
        alpaca_secret = os.getenv("ALPACA_SECRET")
        if not alpaca_key:
            raise ValueError("ALPACA_KEY environment variable is required")
        if not alpaca_secret:
            raise ValueError("ALPACA_SECRET environment variable is required")
        client = TradingClient(alpaca_key, alpaca_secret, paper=True)
        return func(client, *args, **kwargs)

    return wrapper
