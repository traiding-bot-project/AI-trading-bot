"""Decorator for logging in."""

import os
from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeVar

from dotenv import load_dotenv

from alpaca.trading.client import TradingClient

P = ParamSpec("P")
R = TypeVar("R")


def with_alpaca_trading_client(func: Callable[Concatenate[TradingClient, P], R]) -> Callable[P, R]:
    """Provides Alpaca TradingClient authentication decorator."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        load_dotenv()
        alpaca_key = os.getenv("ALPACA_KEY")
        alpaca_secret = os.getenv("ALPACA_SECRET")
        client = TradingClient(alpaca_key, alpaca_secret, paper=True)
        return func(client, *args, **kwargs)

    return wrapper
