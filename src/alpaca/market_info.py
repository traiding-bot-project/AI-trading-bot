import datetime
import os
from typing import Optional

import dotenv

from src.alpaca.common import with_alpaca_trading_client

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.historical import NewsClient # cool, but looks too slow
from alpaca.data.historical import OptionHistoricalDataClient
from alpaca.data.historical import ScreenerClient # 10 most active stocks
from alpaca.data.historical import StockHistoricalDataClient

from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.common.enums import Sort
from alpaca.data.enums import Adjustment, DataFeed


from dotenv import load_dotenv


load_dotenv()

#client_option = OptionHistoricalDataClient()
#client_news = NewsClient()
#client_active_stocks = ScreenerClient()


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
# Convert to dataframe
#print(get_crypto_market_data(["BTC/USD"], TimeFrame.Hour, datetime.datetime(2022, 9, 1), datetime.datetime(2022, 9, 7)))
#print(get_stock_market_data(["TSLA"], TimeFrame.Hour, datetime.datetime(2022, 9, 1), datetime.datetime(2022, 9, 7)))
