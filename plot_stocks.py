import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import datetime

tickers = ["NVDA", "TSLA", "MSFT", "CRDO"]
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=365)

for ticker in tickers:
    data = yf.download(ticker, start=start_date, end=end_date)
    
    close_col = data['Close']
    if isinstance(close_col, pd.DataFrame):
        close_series = close_col[ticker]
    else:
        close_series = close_col
        
    last_close = float(close_series.iloc[-1])
    initial_price = last_close # Base FCN levels on the latest closing price
    last_date = data.index[-1].strftime('%Y-%m-%d')
    last_dt = data.index[-1]
    
    # Calculate FCN levels based on the latest close price
    ko_price = initial_price * 1.00
    ko_pct = 100
    strike_price = initial_price * 0.80
    strike_pct = 80
    ki_price = initial_price * 0.65
    ki_pct = 65
    
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, close_series, label=f'{ticker} Close Price', color='blue')
    
    # Draw FCN lines
    plt.axhline(y=ko_price, color='green', linestyle='--', label='KO (100%)')
    plt.axhline(y=strike_price, color='orange', linestyle='--', label='Strike (80%)')
    plt.axhline(y=ki_price, color='red', linestyle='--', label='KI (65%)')
    
    # Annotate prices and percentages on the plot right edge
    plt.text(last_dt, ko_price, f' KO: {ko_price:.2f} ({ko_pct}%)', color='green', 
             verticalalignment='bottom', horizontalalignment='left', fontsize=10, weight='bold')
    plt.text(last_dt, strike_price, f' Strike: {strike_price:.2f} ({strike_pct}%)', color='orange', 
             verticalalignment='bottom', horizontalalignment='left', fontsize=10, weight='bold')
    plt.text(last_dt, ki_price, f' KI: {ki_price:.2f} ({ki_pct}%)', color='red', 
             verticalalignment='bottom', horizontalalignment='left', fontsize=10, weight='bold')
    
    # Adjust x-axis limit slightly to make room for text
    plt.xlim(data.index[0], data.index[-1] + datetime.timedelta(days=45))
    
    plt.title(f'{ticker} Stock Price with FCN Levels (Past Year)')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    output_path = f'/Users/hughlee/.gemini/antigravity/playground/nascent-einstein/{ticker.lower()}_fcn_current_trend.png'
    plt.savefig(output_path)
    plt.close()
    
    print(f"[{ticker}] KO(100%):{ko_price:.2f}, Strike(80%):{strike_price:.2f}, KI(65%):{ki_price:.2f}")
    print(f"Plot saved to {output_path}")
