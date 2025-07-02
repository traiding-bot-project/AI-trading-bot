"""Create MCP server with components."""

from mcp.server.fastmcp import FastMCP
#from src.alpaca.trading import create_market_order, get_account_info, search_all_assets, get_orders_info, cancel_open_orders, get_all_positions, close_all_positions, create_limit_order
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
import src.alpaca.trading as trading

mcp = FastMCP()

@mcp.tool()
def get_account_info():
    return trading.get_account_info()

@mcp.tool()
def search_all_assets():
    return trading.search_all_assets()

@mcp.tool()
def get_orders_info(status: QueryOrderStatus = QueryOrderStatus.ALL, side: OrderSide | None = None):
    return trading.get_orders_info(status=status, side=side)

@mcp.tool()
def cancel_open_orders():
    return trading.cancel_open_orders()

@mcp.tool()
def get_all_positions():
    return trading.get_all_positions()

@mcp.tool()
def close_all_positions(cancel_orders:bool = False):
    return trading.close_all_positions(cancel_orders)

@mcp.tool()
def create_market_order(symbol: str , qty: float, side: OrderSide = OrderSide.BUY, time_in_force: TimeInForce = TimeInForce.DAY):
    return trading.create_market_order(symbol = symbol, qty = qty, side = side, time_in_force = time_in_force)

@mcp.tool()
def create_limit_order(symbol: str, limit_price: float, notional: float, side: OrderSide = OrderSide.BUY, time_in_force: TimeInForce = TimeInForce.GTC):
    return trading.create_limit_order(symbol = symbol, limit_price = limit_price, notional = notional, side = side, time_in_force = time_in_force)