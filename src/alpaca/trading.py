"""Account manager for Alpaca API."""

from src.alpaca.common import with_alpaca_trading_client
from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.models import Asset, Order, TradeAccount
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetAssetsRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass, AssetStatus, QueryOrderStatus


@with_alpaca_trading_client
def get_acc_info(trading_client) -> TradeAccount | RawData:
    """Get account info from AlpacaAPI."""
    account = trading_client.get_account()
    return account

@with_alpaca_trading_client
def search_all_assets(trading_client: TradingClient, asset_class: AssetClass | None = None, status: AssetStatus | None = None) -> list[Asset] | RawData:
    """Search assets from AlpacaAPI."""
    search_params = GetAssetsRequest(asset_class=asset_class, status=status)
    return trading_client.get_all_assets(search_params)

@with_alpaca_trading_client
def get_orders_info(trading_client: TradingClient, status: QueryOrderStatus = QueryOrderStatus.ALL, side: OrderSide | None = None) -> list[Order] | RawData:
    """Get orders info from AlpacaAPI."""
    request_params = GetOrdersRequest(status=status, side=side)
    return trading_client.get_orders(filter=request_params)

@with_alpaca_trading_client
def cancel_open_orders(trading_client: TradingClient):
    """Cancel all open orders"""
    cancel_statuses = trading_client.cancel_orders()
    return cancel_statuses

@with_alpaca_trading_client
def get_all_positions(trading_client: TradingClient):
    """Return all open positions"""
    positions = trading_client.get_all_positions()
    return positions

@with_alpaca_trading_client
def close_all_positions(trading_client: TradingClient):
    """Close all open positions"""
    cancel_positions = trading_client.close_all_positions(cancel_orders=False)
    return cancel_positions

"""Creating an Order"""

@with_alpaca_trading_client
def market_order(trading_client: TradingClient, symbol: str , qty: float, side: OrderSide = OrderSide.BUY, time_in_force: TimeInForce = TimeInForce.DAY):
    """Buy or sell a stock at the best available price"""
    market_order_data = MarketOrderRequest(
        symbol=symbol, # Ticker symbol
        qty=qty, # Fractional shares
        side=side, # Buying or selling (Buying by default)
        time_in_force=time_in_force # Order expires at market close by default
    )
    submit_market_order = trading_client.submit_order(
        order_data=market_order_data
    )
    return submit_market_order

@with_alpaca_trading_client
def limit_order(trading_client: TradingClient, symbol: str , limit_price: float, notional: float, side: OrderSide = OrderSide.BUY, time_in_force: TimeInForce = TimeInForce.GTC):
    """Buy or sell a stock at a specific price or better"""
    limit_order_data = LimitOrderRequest(
        symbol=symbol, # Ticker symbol
        limit_price=limit_price, # Minimum acceptable price
        notional=notional, #Amount to sell or buy (buy by default)
        side=side, # Buying or selling (Buying by default)
        time_in_force=time_in_force # Fill-or-Kill: Entire order must execute immediately by default
    )
    submit_limit_order = trading_client.submit_order(
        order_data=limit_order_data
    )
    return submit_limit_order
