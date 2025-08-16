"""Test for alpaca functions."""

import os
from unittest.mock import patch, MagicMock
from uuid import uuid4
import pytest

from alpaca.trading.enums import AssetClass, AssetStatus, OrderSide, TimeInForce, AccountStatus
from alpaca.trading.models import Order, TradeAccount
from src.alpaca.common import with_alpaca_trading_client
from src.router.mcp.mcp import (
    close_all_positions,
    create_market_order,
    get_account_info,
    get_all_positions,
    get_orders_info,
    search_all_assets,
    cancel_open_orders,
    create_limit_order
)

from alpaca.common import RawData
from alpaca.trading.enums import AssetClass, AssetStatus, OrderSide, QueryOrderStatus, TimeInForce
from alpaca.trading.models import Asset, ClosePositionResponse, Order, Position, TradeAccount
from alpaca.trading.requests import CancelOrderResponse, CancelOrderResponse

ALPACA_ACCOUNT_NUMBER = "12345"
ALPACA_CRYPTO_ASSETS = [
  {
    "id": "14e09ad6-a301-4e2f-8da9-de3cf45bf80a",
    "class": "crypto",
    "exchange": "CRYPTO",
    "symbol": "USDG/USD",
    "name": "USDG/USD pair",
    "status": "active",
    "tradable": True,
    "marginable": False,
    "maintenance_margin_requirement": 100,
    "margin_requirement_long": "100",
    "margin_requirement_short": "100",
    "shortable": False,
    "easy_to_borrow": False,
    "fractionable": True,
    "attributes": [],
    "min_order_size": "1.00050025",
    "min_trade_increment": "0.000000001"
  },
  {
    "id": "541b0d67-c2c7-4135-ac31-ff2aa6c0dd71",
    "class": "crypto",
    "exchange": "CRYPTO",
    "symbol": "USDT/USD",
    "name": "USD Tether / US Dollar",
    "status": "active",
    "tradable": True,
    "marginable": False,
    "maintenance_margin_requirement": 100,
    "margin_requirement_long": "100",
    "margin_requirement_short": "100",
    "shortable": False,
    "easy_to_borrow": False,
    "fractionable": True,
    "attributes": [],
    "min_order_size": "1.00040016",
    "min_trade_increment": "0.000000001",
    "price_increment": "0.0001"
  },
  {
    "id": "684a2cad-85c3-4e09-ac9d-b8893dd1e02f",
    "class": "crypto",
    "exchange": "CRYPTO",
    "symbol": "USDT/USDC",
    "name": "USD Tether / USD Coin",
    "status": "active",
    "tradable": True,
    "marginable": False,
    "maintenance_margin_requirement": 100,
    "margin_requirement_long": "100",
    "margin_requirement_short": "100",
    "shortable": False,
    "easy_to_borrow": False,
    "fractionable": True,
    "attributes": [],
    "min_order_size": "0.997008973",
    "min_trade_increment": "0.000000001",
    "price_increment": "0.0001"
  },
]
ALPACA_MARKET_ORDER = {
  "id": "533dfcdb-b027-4bfd-94de-61ef8982fa3d",
  "client_order_id": "dde5e66f-a41f-4dbd-b67d-4651143b74ac",
  "created_at": "2025-08-16T15:38:16.620246287Z",
  "updated_at": "2025-08-16T15:38:16.621342867Z",
  "submitted_at": "2025-08-16T15:38:16.620246287Z",
  "filled_at": None,
  "expired_at": None,
  "canceled_at": None,
  "failed_at": None,
  "replaced_at": None,
  "replaced_by": None,
  "replaces": None,
  "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
  "symbol": "AAPL",
  "asset_class": "us_equity",
  "notional": None,
  "qty": "2",
  "filled_qty": "0",
  "filled_avg_price": None,
  "order_class": "",
  "order_type": "market",
  "type": "market",
  "side": "buy",
  "position_intent": "buy_to_open",
  "time_in_force": "day",
  "limit_price": None,
  "stop_price": None,
  "status": "accepted",
  "extended_hours": False,
  "legs": None,
  "trail_percent": None,
  "trail_price": None,
  "hwm": None,
  "subtag": None,
  "source": None,
  "expires_at": "2025-08-18T20:00:00Z"
}
ALPACA_LIMIT_ORDER = {
  "id": "30eb4690-5ce4-4a9e-a2f5-1ecec03c6f54",
  "client_order_id": "c7a51bbe-bb03-47dd-91f9-dfb91af95d17",
  "created_at": "2025-08-16T15:39:48.2064626Z",
  "updated_at": "2025-08-16T15:39:48.20745553Z",
  "submitted_at": "2025-08-16T15:39:48.2064626Z",
  "filled_at": None,
  "expired_at": None,
  "canceled_at": None,
  "failed_at": None,
  "replaced_at": None,
  "replaced_by": None,
  "replaces": None,
  "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
  "symbol": "AAPL",
  "asset_class": "us_equity",
  "notional": None,
  "qty": "2",
  "filled_qty": "0",
  "filled_avg_price": None,
  "order_class": "",
  "order_type": "limit",
  "type": "limit",
  "side": "buy",
  "position_intent": "buy_to_open",
  "time_in_force": "day",
  "limit_price": "150",
  "stop_price": None,
  "status": "accepted",
  "extended_hours": False,
  "legs": None,
  "trail_percent": None,
  "trail_price": None,
  "hwm": None,
  "subtag": None,
  "source": None,
  "expires_at": "2025-08-18T20:00:00Z"
}
ALPACA_EXAMPLE_ORDERS = [
  {
    "id": "30eb4690-5ce4-4a9e-a2f5-1ecec03c6f54",
    "client_order_id": "c7a51bbe-bb03-47dd-91f9-dfb91af95d17",
    "created_at": "2025-08-16T15:39:48.2064626Z",
    "updated_at": "2025-08-16T15:39:48.20745553Z",
    "submitted_at": "2025-08-16T15:39:48.2064626Z",
    "filled_at": None,
    "expired_at": None,
    "canceled_at": None,
    "failed_at": None,
    "replaced_at": None,
    "replaced_by": None,
    "replaces": None,
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "asset_class": "us_equity",
    "notional": None,
    "qty": "2",
    "filled_qty": "0",
    "filled_avg_price": None,
    "order_class": "",
    "order_type": "limit",
    "type": "limit",
    "side": "buy",
    "position_intent": "buy_to_open",
    "time_in_force": "day",
    "limit_price": "150",
    "stop_price": None,
    "status": "accepted",
    "extended_hours": False,
    "legs": None,
    "trail_percent": None,
    "trail_price": None,
    "hwm": None,
    "subtag": None,
    "source": None,
    "expires_at": "2025-08-18T20:00:00Z"
  },
  {
    "id": "533dfcdb-b027-4bfd-94de-61ef8982fa3d",
    "client_order_id": "dde5e66f-a41f-4dbd-b67d-4651143b74ac",
    "created_at": "2025-08-16T15:38:16.620246Z",
    "updated_at": "2025-08-16T15:38:16.621343Z",
    "submitted_at": "2025-08-16T15:38:16.620246Z",
    "filled_at": None,
    "expired_at": None,
    "canceled_at": None,
    "failed_at": None,
    "replaced_at": None,
    "replaced_by": None,
    "replaces": None,
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "asset_class": "us_equity",
    "notional": None,
    "qty": "2",
    "filled_qty": "0",
    "filled_avg_price": None,
    "order_class": "",
    "order_type": "market",
    "type": "market",
    "side": "buy",
    "position_intent": "buy_to_open",
    "time_in_force": "day",
    "limit_price": None,
    "stop_price": None,
    "status": "accepted",
    "extended_hours": False,
    "legs": None,
    "trail_percent": None,
    "trail_price": None,
    "hwm": None,
    "subtag": None,
    "source": "access_key",
    "expires_at": "2025-08-18T20:00:00Z"
  },
  {
    "id": "850805b0-3770-4df9-a579-a54ce99d074d",
    "client_order_id": "101f4f26-ece5-4234-88f5-7fc19705cecf",
    "created_at": "2025-08-16T15:29:30.705662Z",
    "updated_at": "2025-08-16T15:29:30.706116Z",
    "submitted_at": "2025-08-16T15:29:30.705662Z",
    "filled_at": None,
    "expired_at": None,
    "canceled_at": None,
    "failed_at": None,
    "replaced_at": None,
    "replaced_by": None,
    "replaces": None,
    "asset_id": "b28f4066-5c6d-479b-a2af-85dc1a8f16fb",
    "symbol": "SPY",
    "asset_class": "us_equity",
    "notional": None,
    "qty": "0.023",
    "filled_qty": "0",
    "filled_avg_price": None,
    "order_class": "",
    "order_type": "market",
    "type": "market",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "day",
    "limit_price": None,
    "stop_price": None,
    "status": "accepted",
    "extended_hours": False,
    "legs": None,
    "trail_percent": None,
    "trail_price": None,
    "hwm": None,
    "subtag": None,
    "source": "access_key",
    "expires_at": "2025-08-18T20:00:00Z"
  }
]
ALPACA_CANCEL_ORDERS = [
  {
    "id": "140c1707-32c7-49bb-887a-9bfa248db560",
    "status": 200
  },
  {
    "id": "cafe787f-f903-45bc-85f3-45b17192eaa8",
    "status": 200
  }
]
ALPACA_POSITION = [
  {
    "asset_id": "b28f4066-5c6d-479b-a2af-85dc1a8f16fb",
    "symbol": "SPY",
    "exchange": "ARCA",
    "asset_class": "us_equity",
    "asset_marginable": True,
    "qty": "0.023",
    "avg_entry_price": "641.5805",
    "side": "long",
    "market_value": "14.79912",
    "cost_basis": "14.756352",
    "unrealized_pl": "0.042768",
    "unrealized_plpc": "0.0028982772978037",
    "unrealized_intraday_pl": "0",
    "unrealized_intraday_plpc": "0",
    "current_price": "643.44",
    "lastday_price": "643.44",
    "change_today": "0",
    "qty_available": "0.023"
  }
]
ALPACA_CLOSE_POSITIONS = [
  {
    "symbol": "SPY",
    "status": 200,
    "body": {
      "id": "850805b0-3770-4df9-a579-a54ce99d074d",
      "client_order_id": "101f4f26-ece5-4234-88f5-7fc19705cecf",
      "created_at": "2025-08-16T15:29:30.705661679Z",
      "updated_at": "2025-08-16T15:29:30.706115579Z",
      "submitted_at": "2025-08-16T15:29:30.705661679Z",
      "filled_at": None,
      "expired_at": None,
      "canceled_at": None,
      "failed_at": None,
      "replaced_at": None,
      "replaced_by": None,
      "replaces": None,
      "asset_id": "b28f4066-5c6d-479b-a2af-85dc1a8f16fb",
      "symbol": "SPY",
      "asset_class": "us_equity",
      "notional": None,
      "qty": "0.023",
      "filled_qty": "0",
      "filled_avg_price": None,
      "order_class": "",
      "order_type": "market",
      "type": "market",
      "side": "sell",
      "position_intent": "sell_to_close",
      "time_in_force": "day",
      "limit_price": None,
      "stop_price": None,
      "status": "accepted",
      "extended_hours": False,
      "legs": None,
      "trail_percent": None,
      "trail_price": None,
      "hwm": None,
      "subtag": None,
      "source": None,
      "expires_at": "2025-08-18T20:00:00Z"
    }
  }
]


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


def test_get_account_info():
    """Mocking TradeAccount info."""
    response_mock = MagicMock(spec=TradeAccount)
    response_mock.return_value = TradeAccount(id=uuid4(), account_number=ALPACA_ACCOUNT_NUMBER, status=AccountStatus.ACTIVE)
    with (patch("alpaca.trading.client.TradingClient.get_account", response_mock)):
        result = get_account_info()
    assert isinstance(result, TradeAccount)
    assert result.account_number == ALPACA_ACCOUNT_NUMBER
    assert result.status == AccountStatus.ACTIVE


def test_search_all_assets():
    """Mocking search all assets info."""
    response_mock = MagicMock(spec=list[Asset])
    response_mock.return_value = [Asset(**item) for item in ALPACA_CRYPTO_ASSETS]
    with (patch("alpaca.trading.client.TradingClient.get_all_assets", response_mock)):
        result = search_all_assets(AssetClass.CRYPTO, AssetStatus.ACTIVE)
    assert all(isinstance(item, Asset) for item in result)
    assert result[0].exchange == "CRYPTO"
    assert result[0].symbol == "USDG/USD"


def test_get_orders_info():
    """Mocking get orders info."""
    response_mock = MagicMock(spec=list[Order])
    response_mock.return_value = [Order(**item) for item in ALPACA_EXAMPLE_ORDERS]
    with (patch("alpaca.trading.client.TradingClient.get_orders", response_mock)):
        result = get_orders_info()
    assert all(isinstance(item, Order) for item in result)
    assert result[0].symbol == "AAPL"
    assert result[0].limit_price == "150"


def test_cancel_open_orders():
    """Mocking cancel open orders."""
    response_mock = MagicMock(spec=list[CancelOrderResponse])
    response_mock.return_value = [CancelOrderResponse(**item) for item in ALPACA_CANCEL_ORDERS]
    with (patch("alpaca.trading.client.TradingClient.cancel_orders", response_mock)):
        result = cancel_open_orders()
    assert all(isinstance(item, CancelOrderResponse) for item in result)
    assert hasattr(result[0], "id")
    assert hasattr(result[0], "status")


def test_get_all_positions():
    """Mock get all positions."""
    response_mock = MagicMock(spec=list[Position])
    response_mock.return_value = [Position(**item) for item in ALPACA_POSITION]
    with (patch("alpaca.trading.client.TradingClient.get_all_positions", response_mock)):
        result = get_all_positions()
    assert all(isinstance(item, Position) for item in result)
    assert result[0].asset_class == "us_equity"
    assert hasattr(result[0], "asset_id")


def test_close_all_positions():
    """Mock close all positions."""
    response_mock = MagicMock(spec=list[ClosePositionResponse])
    response_mock.return_value = [ClosePositionResponse(**item) for item in ALPACA_CLOSE_POSITIONS]
    with (patch("alpaca.trading.client.TradingClient.close_all_positions", response_mock)):
        result = close_all_positions(cancel_orders=True)
    assert all(isinstance(item, ClosePositionResponse) for item in result)
    assert result[0].body.asset_class == "us_equity"
    assert hasattr(result[0].body, "asset_id")


def test_create_market_order():
    """Mock market order."""
    response_mock = MagicMock(spec=Order)
    response_mock.return_value = Order(**ALPACA_MARKET_ORDER)
    with (patch("alpaca.trading.client.TradingClient.submit_order", response_mock)):
        result = create_market_order(symbol="AAPL", qty=2, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
    assert isinstance(result, Order)
    assert result.asset_class == "us_equity"
    assert result.symbol == "AAPL"
    assert result.order_type == "market"
    assert hasattr(result, "asset_id")


def test_create_limit_order():
    """Mock limit order."""
    response_mock = MagicMock(spec=Order)
    response_mock.return_value = Order(**ALPACA_LIMIT_ORDER)
    with (patch("alpaca.trading.client.TradingClient.submit_order", response_mock)):
        result = create_limit_order(symbol="AAPL", limit_price="150", notional=300, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
    assert isinstance(result, Order)
    assert result.asset_class == "us_equity"
    assert result.symbol == "AAPL"
    assert result.order_type == "limit"
    assert result.limit_price == "150"
    assert hasattr(result, "asset_id")
