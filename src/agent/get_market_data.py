import yfinance as yf

def get_price_data(stocks: str, period: str = "2mo"):
    data = yf.Ticker(stocks)
    return data.history(period=period)

def get_quarterly_income(stocks: str):
    data = yf.Ticker(stocks)
    return data.quarterly_income_stmt
