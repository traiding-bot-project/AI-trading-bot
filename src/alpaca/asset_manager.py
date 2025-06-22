import os

from dotenv import load_dotenv
from alpaca.trading.enums import AssetClass, AssetStatus
from alpaca.trading.models import Asset
from alpaca.trading.requests import GetAssetsRequest
from alpaca.common import RawData
from alpaca.trading.client import TradingClient

load_dotenv()
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)

def search_assets(asset_class: AssetClass | None = None, status: AssetStatus | None = None) -> list[Asset] | RawData:
    """Search assets from AlpacaAPI."""
    search_params = GetAssetsRequest(asset_class=asset_class, status=status)
    return trading_client.get_all_assets(search_params)