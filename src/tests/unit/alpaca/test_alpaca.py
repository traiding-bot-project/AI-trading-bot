"""Test for alpaca functions."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from alpaca.trading.enums import AssetClass, AssetStatus, OrderSide, TimeInForce
from alpaca.trading.models import Order, TradeAccount
from src.alpaca.common import with_alpaca_trading_client
from src.router.mcp.mcp import (
    create_market_order,
    get_account_info,
    get_orders_info,
    search_all_assets,
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


class TestMCPTools(unittest.TestCase):
    """Tests for mcp functions."""

    @patch("src.router.mcp.mcp.get_account_info")
    def test_get_account_info(self, mock_get_account_info):
        """Mocking TradeAccount info."""
        mock_value = SimpleNamespace(account_number="PA382TCF0GFZ", account_blocked=False)
        mock_get_account_info.return_value = mock_value
        result = get_account_info()
        self.assertIsInstance(result, TradeAccount)
        self.assertEqual(result.account_number, "PA382TCF0GFZ")
        self.assertEqual(result.account_blocked, False)

    @patch("src.router.mcp.mcp.search_all_assets")
    def test_search_all_assets(self, mock_search_all_assets):
        """Mocking orders info."""
        mock_value = SimpleNamespace(maintenance_margin_requirement=100.0, min_trade_increment=1e-09)
        mock_search_all_assets.return_value = mock_value
        result = search_all_assets(AssetClass.CRYPTO, AssetStatus.ACTIVE)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0].maintenance_margin_requirement, 100.0)
        self.assertEqual(result[0].min_trade_increment, 1e-09)

    @patch("src.router.mcp.mcp.get_orders_info")
    def test_get_orders_info(self, mock_get_orders_info):
        """Mocking orders info."""
        mock_value = SimpleNamespace(ratio_qty=None, replaced_at=None)
        mock_get_orders_info.return_value = mock_value
        result = get_orders_info()
        self.assertIsInstance(result, list)
        self.assertEqual(result[0].ratio_qty, None)
        self.assertEqual(result[0].replaced_at, None)

    @patch("src.router.mcp.mcp.create_market_order")
    def test_create_market_order(self, mock_create_market_order):
        """Mock market order."""
        mock_value = SimpleNamespace(symbol="SPY", qty="0.023")
        mock_create_market_order.return_value = mock_value
        result = create_market_order(symbol="SPY", qty=0.023, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
        self.assertIsInstance(result, Order)
        self.assertEqual(result.symbol, "SPY")
        self.assertEqual(result.qty, "0.023")
