"""Create MCP server with components."""

from mcp.server.fastmcp import FastMCP

import src.alpaca.trading as trading
from alpaca.trading.enums import AssetClass, AssetStatus, OrderSide, QueryOrderStatus, TimeInForce

mcp = FastMCP()


@mcp.tool()
def get_account_info():
    """Returns the authenticated account information."""
    return trading.get_account_info()


@mcp.tool()
def search_all_assets(asset_class: AssetClass | None = None, status: AssetStatus | None = None):
    """Searches all possible assets."""
    return trading.search_all_assets(asset_class=asset_class, status=status)


@mcp.tool()
def get_orders_info(status: QueryOrderStatus = QueryOrderStatus.ALL, side: OrderSide | None = None):
    """Provides history of orders."""
    return trading.get_orders_info(status=status, side=side)


@mcp.tool()
def cancel_open_orders():
    """Cancel all open orders."""
    return trading.cancel_open_orders()


@mcp.tool()
def get_all_positions():
    """Provides all positions."""
    return trading.get_all_positions()


@mcp.tool()
def close_all_positions(cancel_orders: bool = False):
    """Close all open positions."""
    return trading.close_all_positions(cancel_orders)


@mcp.tool()
def create_market_order(
    symbol: str, qty: float, side: OrderSide = OrderSide.BUY, time_in_force: TimeInForce = TimeInForce.DAY
):
    """Submit a market order."""
    return trading.create_market_order(symbol=symbol, qty=qty, side=side, time_in_force=time_in_force)


@mcp.tool()
def create_limit_order(
    symbol: str,
    limit_price: float,
    notional: float,
    side: OrderSide = OrderSide.BUY,
    time_in_force: TimeInForce = TimeInForce.GTC,
):
    """Submit a limit order."""
    return trading.create_limit_order(
        symbol=symbol, limit_price=limit_price, notional=notional, side=side, time_in_force=time_in_force
    )
