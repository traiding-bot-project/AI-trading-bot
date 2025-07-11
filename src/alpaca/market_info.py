import datetime
import os
from typing import Optional

import pandas as pd

import dotenv

from src.alpaca.common import with_alpaca_trading_client

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.historical import NewsClient
from alpaca.data.historical import StockHistoricalDataClient

from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest, NewsRequest
from alpaca.common.enums import Sort
from alpaca.data.enums import Adjustment, DataFeed


from dotenv import load_dotenv


load_dotenv()

# TODO: other data requests; implement later if needed 
#client_option = OptionHistoricalDataClient()
#client_active_stocks = ScreenerClient() # 10 most active stocks


def get_crypto_market_data (symbol_or_symbols: list, timeframe: TimeFrame, 
                            start: datetime, end: datetime, 
                            limit: (Optional[int])=None,
                            sort: (Optional[Sort])=Sort.DESC):
    client_crypto = CryptoHistoricalDataClient()
    request_params = CryptoBarsRequest(symbol_or_symbols=symbol_or_symbols,
                                    timeframe=timeframe,
                                    start=start,
                                    end=end,
                                    limit=limit,
                                    sort=sort)
    recieved_data = client_crypto.get_crypto_bars(request_params)
    return recieved_data.df


def get_stock_market_data (symbol_or_symbols: list, 
                           timeframe: TimeFrame, 
                            start: datetime, 
                            end: datetime, 
                            limit: (Optional[int])=None,
                            adjustment: (Optional[Adjustment])=None,
                            feed: (Optional[DataFeed])= DataFeed.IEX, # another possible free opiton: DELAYED_SIP
                            sort: (Optional[Sort])=Sort.DESC):
    client_stock = StockHistoricalDataClient(api_key = os.getenv("ALPACA_KEY"), secret_key = os.getenv("ALPACA_SECRET"))
    request_params = StockBarsRequest(symbol_or_symbols=symbol_or_symbols,
                                    timeframe=timeframe,
                                    start=start,
                                    end=end,
                                    limit=limit,
                                    adjustment=adjustment,
                                    feed=feed,
                                    sort=sort)
    recieved_data = client_stock.get_stock_bars(request_params)
    return recieved_data.df


def get_news_data (start: datetime, 
                    end: datetime, 
                    include_content: (Optional[bool]) = True,
                    exclude_contentless: (Optional[bool]) = False,
                    limit: (Optional[int])=None, # Limit of news items to be returned for given page.
                    sort: (Optional[Sort])=Sort.DESC):
    client_news = NewsClient(api_key = os.getenv("ALPACA_KEY"), secret_key = os.getenv("ALPACA_SECRET"))
    request_params = NewsRequest(start=start,
                                    end=end,
                                    include_content=include_content,
                                    exclude_contentless=exclude_contentless,
                                    limit=limit,
                                    sort=sort)
    recieved_data = client_news.get_news(request_params)
    recieved_data_df = recieved_data.df
    return clen_news_df(recieved_data_df)


def clen_news_df(df):
    #if "id" not in df.columns:
    #    df = df.reset_index() # to fix problem with index being auto created by pandas
    #df["full_headline"] = df["id"].astype(str) + " " + df["headline"].astype(str)
    df = df.drop(columns=["source", "url", "images", "summary", "author", "images"])
    return df

