import os
from typing import Union, List, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPACA_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET")


def get_stock_hist_data(stocks: Union[str, List[str]], timeframe: TimeFrame, start: Optional[datetime], end: Optional[datetime]):
    client = StockHistoricalDataClient(api_key=API_KEY, secret_key=SECRET_KEY)
    request_params = StockBarsRequest(
        symbol_or_symbols=stocks,
        timeframe=timeframe,
        start=start,
        end=datetime.today() - relativedelta(months=2)
    )

print(type(datetime.today()))

print(get_stock_hist_data(stocks=["AAPL"], timeframe=TimeFrame.Day, start="2025-10-01", end="2025-08-01"))