import datetime

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.historical import NewsClient # cool, but looks too slow
from alpaca.data.historical import OptionHistoricalDataClient
from alpaca.data.historical import ScreenerClient # 10 most active stocks
from alpaca.data.historical import StockHistoricalDataClient

from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest

client_crypto = CryptoHistoricalDataClient()
client_option = OptionHistoricalDataClient()
client_stock = StockHistoricalDataClient()
client_news = NewsClient()
client_active_stocks = ScreenerClient()




# Creating request object
request_params = CryptoBarsRequest(
  symbol_or_symbols=["BTC/USD"],
  timeframe=TimeFrame.Hour,
  start=datetime.datetime(2022, 9, 1),
  end=datetime.datetime(2022, 9, 7)
)

# Retrieve daily bars for Bitcoin in a DataFrame and printing it
btc_bars = client.get_crypto_bars(request_params)

# Convert to dataframe
print(btc_bars.df)

