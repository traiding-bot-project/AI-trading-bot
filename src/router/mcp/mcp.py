"""Create MCP server with components."""

import datetime

import pandas as pd

import src.alpaca.trading as trading
import src.alpaca.market_info as market_info
from alpaca.common import RawData
from alpaca.common.enums import Sort
from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import (
    AssetClass,
    AssetStatus,
    OrderSide,
    QueryOrderStatus,
    TimeInForce,
)
from alpaca.trading.models import (
    Asset,
    ClosePositionResponse,
    Order,
    Position,
    TradeAccount,
)
from alpaca.trading.requests import CancelOrderResponse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
def get_account_info() -> TradeAccount | RawData:
    """Returns the authenticated account information."""
    return trading.get_account_info()


@mcp.tool()
def search_all_assets(
    asset_class: AssetClass, status: AssetStatus = "active"
) -> list[Asset] | RawData:
    """Searches all possible assets."""
    return trading.search_all_assets(asset_class=asset_class, status=status)


@mcp.tool()
def get_orders_info(
    status: QueryOrderStatus = QueryOrderStatus.ALL, side: OrderSide = OrderSide.BUY
) -> list[Order] | RawData:
    """Provides history of orders."""
    return trading.get_orders_info(status=status, side=side)


@mcp.tool()
def cancel_open_orders() -> list[CancelOrderResponse] | RawData:
    """Cancel all open orders."""
    return trading.cancel_open_orders()


@mcp.tool()
def get_all_positions() -> list[Position] | RawData:
    """Provides all positions."""
    return trading.get_all_positions()


@mcp.tool()
def close_all_positions(
    cancel_orders: bool = False,
) -> list[ClosePositionResponse] | RawData:
    """Close all open positions."""
    return trading.close_all_positions(cancel_orders)


@mcp.tool()
def create_market_order(
    symbol: str,
    qty: float,
    side: OrderSide = OrderSide.BUY,
    time_in_force: TimeInForce = TimeInForce.DAY,
) -> Order | RawData:
    """Submit a market order."""
    return trading.create_market_order(
        symbol=symbol, qty=qty, side=side, time_in_force=time_in_force
    )


@mcp.tool()
def create_limit_order(
    symbol: str,
    limit_price: float,
    notional: float,
    side: OrderSide = OrderSide.BUY,
    time_in_force: TimeInForce = TimeInForce.GTC,
) -> Order | RawData:
    """Submit a limit order."""
    return trading.create_limit_order(
        symbol=symbol,
        limit_price=limit_price,
        notional=notional,
        side=side,
        time_in_force=time_in_force,
    )


@mcp.tool()
def get_crypto_market_data(
    symbol_or_symbols: list,
    timeframe: TimeFrame,
    start: datetime.datetime,
    end: datetime.datetime,
    limit: int | None = None,
    sort: Sort | None = Sort.DESC,
    ) -> pd.DataFrame:
    """Get market data on crypto assets."""
    return market_info.get_crypto_market_data(symbol_or_symbols=symbol_or_symbols,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
        sort=sort,
    )


@mcp.tool()
def get_stock_market_data(
    symbol_or_symbols: list,
    timeframe: TimeFrame,
    start: datetime.datetime,
    end: datetime.datetime,
    limit: int | None = None,
    adjustment: Adjustment | None = None,
    feed: DataFeed | None = DataFeed.IEX,  # another possible free opiton: DELAYED_SIP
    sort: Sort | None = Sort.DESC,
) -> pd.DataFrame:
    """Get data on crypto assets."""
    return market_info.get_stock_market_data(
        symbol_or_symbols=symbol_or_symbols,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
        adjustment=adjustment,
        feed=feed,
        sort=sort,
    )


@mcp.tool()
def get_news_data(
    start: datetime.datetime,
    end: datetime.datetime,
    include_content: bool | None = True,
    exclude_contentless: bool | None = False,
    limit: int | None = None,  # Limit of news items to be returned for given page.
    sort: Sort | None = Sort.DESC,
) -> pd.DataFrame:
    """Download news articles."""
    return market_info.get_news_data(
        start=start,
        end=end,
        include_content=include_content,
        exclude_contentless=exclude_contentless,
        limit=limit,
        sort=sort,
    )