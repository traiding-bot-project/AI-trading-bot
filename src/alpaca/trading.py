"""Account manager for Alpaca API."""

from alpaca.common import RawData
from alpaca.trading.client import TradingClient
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
from alpaca.trading.requests import (
    CancelOrderResponse,
    GetAssetsRequest,
    GetOrdersRequest,
    LimitOrderRequest,
    MarketOrderRequest,
)
from src.alpaca.common import with_alpaca_trading_client


@with_alpaca_trading_client
def get_account_info(trading_client: TradingClient) -> TradeAccount | RawData:
    """Returns the authenticated account information."""
    return trading_client.get_account()


@with_alpaca_trading_client
def search_all_assets(
    trading_client: TradingClient, asset_class: AssetClass, status: AssetStatus
) -> list[Asset] | RawData:
    """Searches all possible assets."""
    return trading_client.get_all_assets(
        GetAssetsRequest(asset_class=asset_class, status=status)
    )


@with_alpaca_trading_client
def get_orders_info(
    trading_client: TradingClient, status: QueryOrderStatus, side: OrderSide
) -> list[Order] | RawData:
    """Provides history of orders."""
    return trading_client.get_orders(filter=GetOrdersRequest(status=status, side=side))


@with_alpaca_trading_client
def cancel_open_orders(
    trading_client: TradingClient,
) -> list[CancelOrderResponse] | RawData:
    """Cancel all open orders."""
    return trading_client.cancel_orders()


@with_alpaca_trading_client
def get_all_positions(trading_client: TradingClient) -> list[Position] | RawData:
    """Provides all positions."""
    return trading_client.get_all_positions()


@with_alpaca_trading_client
def close_all_positions(
    trading_client: TradingClient, cancel_orders: bool
) -> list[ClosePositionResponse] | RawData:
    """Close all open positions."""
    return trading_client.close_all_positions(cancel_orders=cancel_orders)


@with_alpaca_trading_client
def create_market_order(
    trading_client: TradingClient,
    symbol: str,
    qty: float,
    side: OrderSide,
    time_in_force: TimeInForce,
) -> Order | RawData:
    """Submit a market order."""
    market_order_data = MarketOrderRequest(
        symbol=symbol, qty=qty, side=side, time_in_force=time_in_force
    )
    return trading_client.submit_order(order_data=market_order_data)


@with_alpaca_trading_client
def create_limit_order(
    trading_client: TradingClient,
    symbol: str,
    limit_price: float,
    notional: float,
    side: OrderSide,
    time_in_force: TimeInForce,
) -> Order | RawData:
    """Submit a limit order."""
    limit_order_data = LimitOrderRequest(
        symbol=symbol,
        limit_price=limit_price,
        notional=notional,
        side=side,
        time_in_force=time_in_force,
    )
    return trading_client.submit_order(order_data=limit_order_data)


# print(search_all_assets(asset_class="crypto", status="active"))
