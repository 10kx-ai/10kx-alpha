# not complete...
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import *
from yahoo_fin import stock_info as si
import numpy as np

pd.options.display.float_format = '{:.2f}'.format

stock_list = si.tickers_sp500()

end_date = date.today()
start_date = end_date - pd.DateOffset(1)

sdf = yf.download(tickers = stock_list, start=start_date, end=end_date, interval="5m")
print(df)
# sdf = yf.download(tickers = ["NVDA", "AAPL"], start=start_date, end=end_date, interval="5m")
# df = sdf[["Close", "Volume"]].stack()
# df.describe()



# Calculating whether the stock closed higher or lower than the previous close
df['PreviousClose'] = df.groupby('Symbols')['Close'].shift(1)
df['is_advancing_issue'] = df['Close'] > df['PreviousClose']

# Calculating advance and decline volumes for each row
df['advance_volume'] = df['Volume'] * df['is_advancing_issue']
df['decline_volume'] = df['Volume'] * (~df['is_advancing_issue'])

# Summing the advance and decline volumes for all symbols at each time step
interval_totals = df.groupby('Date').agg({'advance_volume': 'sum', 'decline_volume': 'sum'})

# Cumulative sum of interval totals
interval_totals['cumulative_uvol'] = interval_totals['advance_volume'].cumsum()
interval_totals['cumulative_dvol'] = interval_totals['decline_volume'].cumsum()

# Merging the cumulative volumes back to the original DataFrame
df = df.merge(interval_totals[['cumulative_uvol', 'cumulative_dvol']], on='Date', how='left')

