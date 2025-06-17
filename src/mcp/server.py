import os
import logging
from typing import Optional, Union, UUID, Order, Dict, Any

from mcp.server.fastmcp import FastMCP
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.models import ClosePositionRequest
from dotenv import load_dotenv

from utils.custom_logger import CustomFormatter

# custom logs
log = logging.getLogger("__name__")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
log.addHandler(ch)

load_dotenv()
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
if not ALPACA_KEY:
    log.error("Wrong Alpaca API key")
if not ALPACA_SECRET:
    log.error("Wrong Alpaca secret")

# local or remote server access
TRANSPORT = "studio"  # or "ssh"

# alpaca api: paper means test acc
trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)


class MCPRouter:
    def __init__(self):
        pass
    mcp = FastMCP(
        name="TraidingBot", 
        host="0.0.0.0", 
        port=os.getenv("MCP_PORT"))  # for HTTP servers


    @mcp.tool()
    def buyAsset(
        symbol: str,
        side: OrderSide,
        time_in_force: TimeInForce,
        qty: Optional[float] = None,
        notional: Optional[float] = None,
    ):
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=side,
            time_in_force=time_in_force,
        )
        return trading_client.submit_order(order_data=market_order_data)


    @mcp.tool()
    def sellAsset(
        symbol_or_asset_id: Union[UUID, str],
        qty: Optional[str] = None,
        percentage: Optional[str] = None,
    ) -> Union[Order, Dict[str, Any]]:
        close_positions_data = ClosePositionRequest(qty=qty, percentage=percentage)
        return trading_client.close_position(symbol_or_asset_id=symbol_or_asset_id, close_options=close_positions_data)


    if __name__ == "__main__":
        if TRANSPORT == "studio":
            mcp.run(transport="studio")
        elif TRANSPORT == "sse":
            mcp.run(transport="sse")
        else:
            raise ValueError(f"Unknown transport: {TRANSPORT}")
