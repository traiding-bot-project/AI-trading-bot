"""Test for alpaca functions."""

import os
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from alpaca.trading.enums import AccountStatus, AssetClass, AssetStatus, OrderSide, TimeInForce
from alpaca.trading.models import Asset, ClosePositionResponse, Order, Position, TradeAccount
from alpaca.trading.requests import CancelOrderResponse
from src.alpaca.common import with_alpaca_trading_client
from src.router.mcp.mcp import (
    cancel_open_orders,
    close_all_positions,
    create_limit_order,
    create_market_order,
    get_account_info,
    get_all_positions,
    get_orders_info,
    search_all_assets,
)
from src.tests.unit.alpaca.common import (
    ALPACA_ACCOUNT_NUMBER,
    ALPACA_CANCEL_ORDERS,
    ALPACA_CLOSE_POSITIONS,
    ALPACA_CRYPTO_ASSETS,
    ALPACA_EXAMPLE_ORDERS,
    ALPACA_LIMIT_ORDER,
    ALPACA_MARKET_ORDER,
    ALPACA_POSITION,
)


def dummy_function(client, *args, **kwargs):
    """Create function for testing decorator."""
    return "success"


@pytest.fixture
def decorated_func():
    """Tested decorator."""
    return with_alpaca_trading_client(dummy_function)


@patch.dict(os.environ, {"ALPACA_KEY": "", "ALPACA_SECRET": ""}, clear=True)
def test_missing_both_vars(decorated_func):
    """Missing environmental variables."""
    with pytest.raises(ValueError, match="ALPACA_KEY environment variable is required"):
        decorated_func()


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_existing_both_vars(decorated_func):
    """Environmental variables exist."""
    assert decorated_func() == "success"


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_get_account_info():
    """Mocking TradeAccount info."""
    response_mock = MagicMock(spec=TradeAccount)
    response_mock.return_value = TradeAccount(
        id=uuid4(), account_number=ALPACA_ACCOUNT_NUMBER, status=AccountStatus.ACTIVE
    )
    with patch("alpaca.trading.client.TradingClient.get_account", response_mock):
        result = get_account_info()
    assert isinstance(result, TradeAccount)
    assert result.account_number == ALPACA_ACCOUNT_NUMBER
    assert result.status == AccountStatus.ACTIVE


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_search_all_assets():
    """Mocking search all assets info."""
    response_mock = MagicMock(spec=list[Asset])
    response_mock.return_value = [Asset(**item) for item in ALPACA_CRYPTO_ASSETS]
    with patch("alpaca.trading.client.TradingClient.get_all_assets", response_mock):
        result = search_all_assets(AssetClass.CRYPTO, AssetStatus.ACTIVE)
    assert all(isinstance(item, Asset) for item in result)
    assert result[0].exchange == "CRYPTO"
    assert result[0].symbol == "USDG/USD"


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_get_orders_info():
    """Mocking get orders info."""
    response_mock = MagicMock(spec=list[Order])
    response_mock.return_value = [Order(**item) for item in ALPACA_EXAMPLE_ORDERS]
    with patch("alpaca.trading.client.TradingClient.get_orders", response_mock):
        result = get_orders_info()
    assert all(isinstance(item, Order) for item in result)
    assert result[0].symbol == "AAPL"
    assert result[0].limit_price == "150"


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_cancel_open_orders():
    """Mocking cancel open orders."""
    response_mock = MagicMock(spec=list[CancelOrderResponse])
    response_mock.return_value = [CancelOrderResponse(**item) for item in ALPACA_CANCEL_ORDERS]
    with patch("alpaca.trading.client.TradingClient.cancel_orders", response_mock):
        result = cancel_open_orders()
    assert all(isinstance(item, CancelOrderResponse) for item in result)
    assert hasattr(result[0], "id")
    assert hasattr(result[0], "status")


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_get_all_positions():
    """Mock get all positions."""
    response_mock = MagicMock(spec=list[Position])
    response_mock.return_value = [Position(**item) for item in ALPACA_POSITION]
    with patch("alpaca.trading.client.TradingClient.get_all_positions", response_mock):
        result = get_all_positions()
    assert all(isinstance(item, Position) for item in result)
    assert result[0].asset_class == "us_equity"
    assert hasattr(result[0], "asset_id")


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_close_all_positions():
    """Mock close all positions."""
    response_mock = MagicMock(spec=list[ClosePositionResponse])
    response_mock.return_value = [ClosePositionResponse(**item) for item in ALPACA_CLOSE_POSITIONS]
    with patch("alpaca.trading.client.TradingClient.close_all_positions", response_mock):
        result = close_all_positions(cancel_orders=True)
    assert all(isinstance(item, ClosePositionResponse) for item in result)
    assert result[0].body.asset_class == "us_equity"
    assert hasattr(result[0].body, "asset_id")


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_create_market_order():
    """Mock market order."""
    response_mock = MagicMock(spec=Order)
    response_mock.return_value = Order(**ALPACA_MARKET_ORDER)
    with patch("alpaca.trading.client.TradingClient.submit_order", response_mock):
        result = create_market_order(symbol="AAPL", qty=2, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
    assert isinstance(result, Order)
    assert result.asset_class == "us_equity"
    assert result.symbol == "AAPL"
    assert result.order_type == "market"
    assert hasattr(result, "asset_id")


@patch.dict(os.environ, {"ALPACA_KEY": "test_key", "ALPACA_SECRET": "test_secret"}, clear=True)
def test_create_limit_order():
    """Mock limit order."""
    response_mock = MagicMock(spec=Order)
    response_mock.return_value = Order(**ALPACA_LIMIT_ORDER)
    with patch("alpaca.trading.client.TradingClient.submit_order", response_mock):
        result = create_limit_order(
            symbol="AAPL", limit_price="150", notional=300, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
        )
    assert isinstance(result, Order)
    assert result.asset_class == "us_equity"
    assert result.symbol == "AAPL"
    assert result.order_type == "limit"
    assert result.limit_price == "150"
    assert hasattr(result, "asset_id")
