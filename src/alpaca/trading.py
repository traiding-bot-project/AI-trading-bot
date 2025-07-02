"""Account manager for Alpaca API."""

from src.alpaca.common import with_alpaca_trading_client
from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.models import Asset, Order, TradeAccount
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetAssetsRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass, AssetStatus, QueryOrderStatus


@with_alpaca_trading_client
def get_account_info(trading_client: TradingClient) -> TradeAccount | RawData:
    return trading_client.get_account()

@with_alpaca_trading_client
def search_all_assets(trading_client: TradingClient, asset_class: AssetClass | None = None, status: AssetStatus | None = None) -> list[Asset] | RawData:
    search_params = GetAssetsRequest(asset_class=asset_class, status=status)
    return trading_client.get_all_assets(search_params)

@with_alpaca_trading_client
def get_orders_info(trading_client: TradingClient, status: QueryOrderStatus, side: OrderSide | None = None) -> list[Order] | RawData:
    return trading_client.get_orders(filter=GetOrdersRequest(status=status, side=side))

@with_alpaca_trading_client
def cancel_open_orders(trading_client: TradingClient):
    return trading_client.cancel_orders()

@with_alpaca_trading_client
def get_all_positions(trading_client: TradingClient):
    return trading_client.get_all_positions()

@with_alpaca_trading_client
def close_all_positions(trading_client: TradingClient, cancel_orders: bool):
    return trading_client.close_all_positions(cancel_orders=cancel_orders)

@with_alpaca_trading_client
def create_market_order(trading_client: TradingClient, symbol: str , qty: float, side: OrderSide, time_in_force: TimeInForce):
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=time_in_force
    )
    return trading_client.submit_order(order_data=market_order_data)

@with_alpaca_trading_client
def create_limit_order(trading_client: TradingClient, symbol: str , limit_price: float, notional: float, side: OrderSide, time_in_force: TimeInForce):
    limit_order_data = LimitOrderRequest(
        symbol=symbol,
        limit_price=limit_price,
        notional=notional,
        side=side,
        time_in_force=time_in_force
    )
    return trading_client.submit_order(order_data=limit_order_data)