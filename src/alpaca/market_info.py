"""Get market data on assets from alpac API."""

import datetime
import os

import pandas as pd
from dotenv import load_dotenv

from alpaca.common.enums import Sort
from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.historical import CryptoHistoricalDataClient, NewsClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, NewsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()

# other data requests; implement later if needed

# client_option = OptionHistoricalDataClient()
# client_active_stocks = ScreenerClient() # 10 most active stocks


def get_crypto_market_data(
    symbol_or_symbols: list,
    timeframe: TimeFrame,
    start: datetime.datetime,
    end: datetime.datetime,
    limit: int | None = None,
    sort: Sort | None = Sort.DESC,
) -> pd.DataFrame:
    """Get data on crypto assets."""
    client_crypto = CryptoHistoricalDataClient()
    request_params = CryptoBarsRequest(
        symbol_or_symbols=symbol_or_symbols,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
        sort=sort,
    )
    recieved_data = client_crypto.get_crypto_bars(request_params)
    return recieved_data.df


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
    client_stock = StockHistoricalDataClient(
        api_key=os.getenv("ALPACA_KEY"), secret_key=os.getenv("ALPACA_SECRET")
    )
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol_or_symbols,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
        adjustment=adjustment,
        feed=feed,
        sort=sort,
    )
    recieved_data = client_stock.get_stock_bars(request_params)
    return recieved_data.df


def get_news_data(
    start: datetime.datetime,
    end: datetime.datetime,
    include_content: bool | None = True,
    exclude_contentless: bool | None = False,
    limit: int | None = None,  # Limit of news items to be returned for given page.
    sort: Sort | None = Sort.DESC,
) -> pd.DataFrame:
    """Download news articles."""
    client_news = NewsClient(
        api_key=os.getenv("ALPACA_KEY"), secret_key=os.getenv("ALPACA_SECRET")
    )
    request_params = NewsRequest(
        start=start,
        end=end,
        include_content=include_content,
        exclude_contentless=exclude_contentless,
        limit=limit,
        sort=sort,
    )
    recieved_data = client_news.get_news(request_params)
    recieved_data_df = recieved_data.df
    return clen_news_df(recieved_data_df)


def clen_news_df(df: pd.DataFrame) -> pd.DataFrame:
    """Dataframe contains columns we don't need."""
    df = df.drop(columns=["source", "url", "images", "summary", "author", "images"])
    return df
