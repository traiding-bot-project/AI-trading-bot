"""Create MCP server with components."""

from mcp.server.fastmcp import FastMCP
from src.alpaca.trading import market_order, get_acc_info, search_all_assets, get_orders_info, cancel_open_orders, get_all_positions, close_all_positions, limit_order
from alpaca.trading.enums import OrderSide, TimeInForce

mcp = FastMCP()

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource."""
    return f"Resource echo: {message}"


@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool."""
    return f"Tool echo: {message}"


@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt."""
    return f"Please process this message: {message}"

@mcp.tool()
def get_account_info():
    """Access details about brokerage account"""
    account_info = get_acc_info()
    return account_info

@mcp.tool()
def search_assets():
    """Provide a list of all available assets"""
    all_assets = search_all_assets()
    return all_assets

@mcp.tool()
def get_orders_history():
    """return all the orders associated with the account."""
    orders_history = get_orders_info()
    return orders_history

@mcp.tool()
def cancel_orders():
    """Cancel all open orders"""
    canceled_orders = cancel_open_orders()
    return canceled_orders

@mcp.tool()
def get_positions():
    """Return all open positions"""
    all_positions = get_all_positions()
    return all_positions

@mcp.tool()
def close_positions():
    """Close all open positions"""
    closed_positions = close_all_positions()
    return closed_positions

@mcp.tool()
def create_market_order(symbol: str , qty: float, side: OrderSide = OrderSide.BUY, time_in_force: TimeInForce = TimeInForce.DAY):
    """Buy or sell a stock at the best available price"""
    submit_market_order = market_order(symbol = symbol, qty = qty, side = side, time_in_force = time_in_force)
    return submit_market_order

@mcp.tool()
def create_limit_order(symbol: str , limit_price: float, notional: float, side: OrderSide = OrderSide.BUY, time_in_force: TimeInForce = TimeInForce.GTC):
    """Buy or sell a stock at a specific price or better"""
    submit_limit_order = limit_order(symbol = symbol, limit_price = limit_price, notional = notional, side = side, time_in_force = time_in_force)
    return submit_limit_order