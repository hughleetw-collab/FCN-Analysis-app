import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import datetime

ticker = "NVDA"
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=365)

data = yf.download(ticker, start=start_date, end=end_date)

# Safe extraction of Close price series
close_col = data['Close']
if isinstance(close_col, pd.DataFrame):
    close_series = close_col[ticker]
else:
    close_series = close_col

last_close = float(close_series.iloc[-1])
last_date = data.index[-1].strftime('%Y-%m-%d')

print(f"---LAST_CLOSE_START---")
print(f"Date: {last_date}, Close: {last_close:.2f}")
print(f"---LAST_CLOSE_END---")

plt.figure(figsize=(12, 6))
plt.plot(data.index, close_series, label='NVDA Close Price', color='blue')
plt.title('NVDA Stock Price - Past Year')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.grid(True)
plt.legend()
plt.tight_layout()
output_path = '/Users/hughlee/.gemini/antigravity/playground/nascent-einstein/nvda_stock_trend.png'
plt.savefig(output_path)
print(f"Plot saved to {output_path}")
