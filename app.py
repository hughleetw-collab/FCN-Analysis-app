import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
import numpy as np
import io
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests
from yahooquery import Ticker

# Set page config
st.set_page_config(page_title="FCN 結構型商品分析報告", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for premium dark theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f1123 0%, #1a1b35 100%);
        color: #e2e8f0;
        font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* Hide Streamlit default header */
    .stApp > header {
        background-color: transparent !important;
    }
    
    /* Top banner */
    .top-banner {
        background: linear-gradient(90deg, #1f224a 0%, #2f336b 100%);
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #3c407a;
    }
    
    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #60a5fa;
        margin-bottom: 5px;
        letter-spacing: 2px;
    }
    
    .sub-title {
        font-size: 13px;
        color: #94a3b8;
        letter-spacing: 2.5px;
    }
    
    .date-info {
        font-size: 11px;
        color: #64748b;
        margin-top: 15px;
    }
    
    /* Global metrics bar */
    .global-metrics {
        background-color: #1a1c38;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 30px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 50px;
        border: 1px solid #2d3160;
    }
    
    .metric-item { text-align: center; }
    .metric-label { font-size: 12px; color: #94a3b8; margin-bottom: 8px; }
    
    .v-ako { font-size: 26px; font-weight: bold; color: #34d399; }
    .v-k { font-size: 26px; font-weight: bold; color: #ef4444; }
    .v-eki { font-size: 26px; font-weight: bold; color: #f59e0b; }
    .v-yield { font-size: 26px; font-weight: bold; color: #a855f7; }
    .v-tickers { font-size: 20px; font-weight: bold; color: #60a5fa; }
    
    /* Card structural styling */
    .stock-card {
        background-color: #1a1c38;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3160;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .card-ticker { font-size: 22px; font-weight: bold; color: #60a5fa; }
    .card-spot { font-size: 13px; color: #cbd5e1; }
    
    /* Chart container */
    .chart-container {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 15px;
    }
    
    /* Bottom metrics inside card */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .m-box {
        background-color: #131429;
        padding: 12px 8px;
        border-radius: 8px;
    }
    
    .m-label { font-size: 11px; color: #64748b; margin-bottom: 6px;}
    .m-val-ako { font-size: 18px; font-weight: 800; color: #34d399; margin-bottom: 3px;}
    .m-val-k { font-size: 18px; font-weight: 800; color: #ef4444; margin-bottom: 3px;}
    .m-val-eki { font-size: 18px; font-weight: 800; color: #f59e0b; margin-bottom: 3px;}
    .m-pct { font-size: 11px; color: #475569; }
    
    /* Card footer */
    .card-footer {
        font-size: 11px;
        color: #64748b;
        display: flex;
        justify-content: space-between;
        border-top: 1px solid #2d3160;
        padding-top: 15px;
        margin-top: auto;
    }
    .f-val { color: #f1f5f9; font-weight: bold; }
    
</style>
""", unsafe_allow_html=True)

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("⚙️ 參數設定")
    tickers_input = st.text_input("掛勾標的 (逗號分隔)", value="TSLA, PLTR, AMD")
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    st.subheader("FCN 條件設定 (%)")
    yield_val = st.number_input("預期收益率 (%)", min_value=0.0, max_value=200.0, value=12.0, step=0.1)
    ako_pct = st.number_input("AKO 敲出價 (%)", min_value=50, max_value=200, value=105, step=1)
    k_pct = st.number_input("K 履約價 (%)", min_value=10, max_value=150, value=80, step=1)
    eki_pct = st.number_input("EKI 歐式敲入 (%)", min_value=10, max_value=150, value=55, step=1)
    
    generate_btn = st.button("更新報告", type="primary")

today_str = datetime.datetime.now().strftime('%Y-%m-%d')
tickers_str = " / ".join(tickers)

# --- Top Dashboard Area ---
st.markdown(f"""
<div class="top-banner">
    <div class="main-title">■ FCN 結構型商品分析報告</div>
    <div class="sub-title">FIXED COUPON NOTE — BARRIER ANALYSIS</div>
    <div class="date-info">報告日期：{today_str} | 資料來源：Yahoo Finance</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="global-metrics">
    <div class="metric-item">
        <div class="metric-label">預期收益率</div>
        <div class="v-yield">{yield_val:.1f}%</div>
    </div>
    <div style="width: 1px; height: 50px; background-color: #2d3160;"></div>
    <div class="metric-item">
        <div class="metric-label">AKO 敲出價</div>
        <div class="v-ako">{ako_pct}%</div>
    </div>
    <div class="metric-item">
        <div class="metric-label">K 履約價</div>
        <div class="v-k">{k_pct}%</div>
    </div>
    <div class="metric-item">
        <div class="metric-label">EKI 歐式敲入</div>
        <div class="v-eki">{eki_pct}%</div>
    </div>
    <div style="width: 1px; height: 50px; background-color: #2d3160;"></div>
    <div class="metric-item">
        <div class="metric-label">掛勾標的</div>
        <div class="v-tickers">{tickers_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Fetch Data & Render ---
if not tickers:
    st.warning("請在側邊欄輸入股票代碼。")
else:
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365)
    
    stock_data = {}
    stock_info = {}
    
    valid_tickers = []
    
    with st.spinner('正在獲取最新市場庫存與價格數據...'):
        for ticker in tickers:
            try:
                # Use yahooquery instead of yfinance for better rate limit handling
                tkr = Ticker(ticker)
                
                # Retrieve 1 year of historical data
                data_dict = tkr.history(period='1y')
                
                # yahooquery returns a MultiIndex dataframe (symbol, date) if successful
                if isinstance(data_dict, pd.DataFrame) and not data_dict.empty:
                    # Reset index to easily work with the 'date' column
                    data = data_dict.reset_index()
                    # Filter just for this ticker (in case it returns multiple, though it shouldn't here)
                    data = data[data['symbol'] == ticker]
                    # Set date back as index, ensure DatetimeIndex
                    data.set_index('date', inplace=True)
                    data.index = pd.to_datetime(data.index)
                    
                    # Compute MAs
                    # yahooquery uses lowercase columns: open, high, low, close, volume, adjclose
                    data['MA50'] = data['close'].rolling(window=50).mean()
                    data['EMA200'] = data['close'].ewm(span=200, adjust=False).mean()
                    
                    stock_data[ticker] = data
                    
                    # Store info using summary_detail or calculate it from history
                    pe_val, mc_val = 'N/A', 'N/A'
                    debug_logs = []
                    
                    try:
                        summary = tkr.summary_detail
                        if isinstance(summary, dict) and ticker in summary and isinstance(summary[ticker], dict):
                            info = summary[ticker]
                            pe_val = info.get('trailingPE', info.get('forwardPE', 'N/A'))
                            mc_val = info.get('marketCap', 'N/A')
                        else:
                            # Fallback to price endpoint
                            price_data = tkr.price
                            if isinstance(price_data, dict) and ticker in price_data and isinstance(price_data[ticker], dict):
                                mc_val = price_data[ticker].get('marketCap', 'N/A')
                    except Exception as info_e:
                        debug_logs.append(f"yq error: {info_e}")
                        
                    # Alpha Vantage Fallback (Using User API Key)
                    if pe_val == 'N/A' or mc_val == 'N/A':
                        try:
                            import requests as std_requests
                            av_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey=CYW0ZERXVLCU6XAH'
                            av_res = std_requests.get(av_url, timeout=5)
                            if av_res.status_code == 200:
                                av_data = av_res.json()
                                if mc_val == 'N/A' and av_data.get('MarketCapitalization') not in [None, 'None']:
                                    mc_val = float(av_data.get('MarketCapitalization'))
                                if pe_val == 'N/A' and av_data.get('PERatio') not in [None, 'None']:
                                    pe_val = float(av_data.get('PERatio'))
                            else:
                                debug_logs.append(f"av code: {av_res.status_code}")
                                if av_res.status_code != 200:
                                    debug_logs.append(av_res.text[:100])
                        except Exception as av_e:
                            debug_logs.append(f"av error: {av_e}")
                        
                    # Absolute Fallback: Yahoo Finance HTML Scraper
                    if pe_val == 'N/A' or mc_val == 'N/A':
                        try:
                            yf_url = f'https://finance.yahoo.com/quote/{ticker}'
                            yf_headers = {'User-Agent': 'Mozilla/5.0'}
                            yf_res = cffi_requests.get(yf_url, impersonate='chrome', headers=yf_headers, timeout=5)
                            soup = BeautifulSoup(yf_res.text, 'html.parser')
                            for li in soup.find_all('li'):
                                text = li.text.lower()
                                if mc_val == 'N/A' and 'market cap' in text and 'intraday' in text:
                                    mc_val = li.text.split('intraday)')[-1].strip()
                                if pe_val == 'N/A' and 'pe ratio' in text.replace('/', '') and '(ttm)' in text:
                                    pe_val = li.text.split('(TTM)')[-1].strip()
                        except Exception as yf_e:
                            debug_logs.append(f"yf scraper error: {yf_e}")
                            
                    # Calculate true 52W high and low from the 1y history we just downloaded successfully!
                    high_val = data['high'].max() if not data.empty else 'N/A'
                    low_val = data['low'].min() if not data.empty else 'N/A'
                    
                    stock_info[ticker] = {
                        '52w_high': high_val,
                        '52w_low': low_val,
                        'pe': pe_val,
                        'market_cap': mc_val,
                        'debug': " | ".join(debug_logs)
                    }
                    valid_tickers.append(ticker)
            except Exception as e:
                st.error(f"{ticker} 發生錯誤 (可能為遠端抓取限制): {str(e)}")
                
    if not stock_data:
        st.error("選定股票的所有資料皆無法獲取！")
    else:
        # Create columns (3 per row)
        cols_per_row = 3
        for i in range(0, len(valid_tickers), cols_per_row):
            cols = st.columns(cols_per_row)
            row_tickers = valid_tickers[i:i+cols_per_row]
            
            for j, ticker in enumerate(row_tickers):
                data = stock_data[ticker]
                s_info = stock_info[ticker]
                
                last_close = float(data['close'].iloc[-1])
                
                ako_price = last_close * (ako_pct / 100.0)
                k_price = last_close * (k_pct / 100.0)
                eki_price = last_close * (eki_pct / 100.0)
                
                # Format metrics
                mc = s_info['market_cap']
                mc_str = "N/A"
                if mc != 'N/A':
                    if isinstance(mc, str):
                        mc = mc.replace(',', '')
                        if 'T' in mc:
                            try: mc_str = f"${float(mc.replace('T', '')) * 1000:.1f}B"
                            except: mc_str = f"${mc}"
                        elif 'B' in mc:
                            mc_str = f"${mc}"
                        elif 'M' in mc:
                            mc_str = f"${mc}"
                        else:
                            try:
                                mc_val = float(mc)
                                mc_str = f"${mc_val/1e9:.1f}B" if mc_val >= 1e9 else (f"${mc_val/1e6:.1f}M" if mc_val >= 1e6 else f"${mc_val}")
                            except: mc_str = mc
                    else:
                        try:
                            mc_val = float(mc)
                            mc_str = f"${mc_val/1e9:.1f}B" if mc_val >= 1e9 else (f"${mc_val/1e6:.1f}M" if mc_val >= 1e6 else f"${mc_val}")
                        except:
                            mc_str = str(mc)
                            
                pe = s_info['pe']
                try:
                    pe_str = f"{float(str(pe).replace(',', '')):.2f}" if pe != 'N/A' else "N/A"
                except (ValueError, TypeError):
                    pe_str = str(pe)
                
                high_val = s_info['52w_high']
                high_str = f"${high_val:.2f}" if isinstance(high_val, float) else high_val
                
                low_val = s_info['52w_low']
                low_str = f"${low_val:.2f}" if isinstance(low_val, float) else low_val

                # Build Plotly Chart
                fig = go.Figure()
                
                # Candlestick chart
                fig.add_trace(go.Candlestick(
                    x=data.index, open=data['open'], high=data['high'], low=data['low'], close=data['close'],
                    name='K Line', increasing_line_color='#22c55e', decreasing_line_color='#ef4444',
                    increasing_fillcolor='#22c55e', decreasing_fillcolor='#ef4444', line_width=1
                ))
                
                # MAs
                fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], mode='lines', name='MA50', line=dict(color='#eab308', width=1.5)))
                fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], mode='lines', name='EMA200', line=dict(color='#3b82f6', width=1.5)))
                
                # FCN Barriers
                fig.add_hline(y=ako_price, line_dash="dash", line_color="#34d399", annotation_text=f"AKO ${ako_price:.2f}", annotation_position="right", annotation_font_color="#34d399", annotation_font_size=11)
                fig.add_hline(y=k_price, line_dash="dash", line_color="#ef4444", annotation_text=f"K ${k_price:.2f}", annotation_position="right", annotation_font_color="#ef4444", annotation_font_size=11)
                fig.add_hline(y=eki_price, line_dash="dash", line_color="#f59e0b", annotation_text=f"EKI ${eki_price:.2f}", annotation_position="right", annotation_font_color="#f59e0b", annotation_font_size=11)
                
                fig.update_layout(
                    title=dict(text=f"<b>{ticker} Daily K-Line & FCN Barriers (1Y)</b>", font=dict(size=12, color='black'), x=0.5, y=0.95),
                    margin=dict(l=10, r=40, t=35, b=10),
                    height=280,
                    showlegend=False,
                    xaxis_rangeslider_visible=False,
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(
                        showgrid=True, 
                        gridcolor='#f1f5f9', 
                        tickfont=dict(size=10, color="#64748b"),
                        range=[data.index.min(), data.index.max() + pd.Timedelta(days=90)]
                    ),
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=10, color="#64748b"), side='right')
                )
                
                # Render UI using Streamlit containers to mimic the stock-card
                with cols[j]:
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: #1a1c38; border-radius: 12px; padding: 20px; border: 1px solid #2d3160; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <div style="font-size: 22px; font-weight: bold; color: #60a5fa;">{ticker}</div>
                                <div style="font-size: 13px; color: #cbd5e1;">Initial Spot: <b>${last_close:.2f}</b></div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        st.markdown(f"""
<div class="metrics-grid">
    <div class="m-box">
        <div class="m-label">AKO (敲出)</div>
        <div class="m-val-ako">${ako_price:.2f}</div>
        <div class="m-pct">{ako_pct}%</div>
    </div>
    <div class="m-box">
        <div class="m-label">K (履約)</div>
        <div class="m-val-k">${k_price:.2f}</div>
        <div class="m-pct">{k_pct}%</div>
    </div>
    <div class="m-box">
        <div class="m-label">EKI (敲入)</div>
        <div class="m-val-eki">${eki_price:.2f}</div>
        <div class="m-pct">{eki_pct}%</div>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; padding-top: 15px; border-top: 1px solid #334155;">
    <div style="display: flex; gap: 20px;">
        <div><span style="color: #94a3b8; font-size: 0.85rem;">52W High</span><br><span style="color: #f8fafc; font-weight: 500;">{high_str}</span></div>
        <div><span style="color: #94a3b8; font-size: 0.85rem;">52W Low</span><br><span style="color: #f8fafc; font-weight: 500;">{low_str}</span></div>
    </div>
    <div style="display: flex; gap: 20px; text-align: right;">
        <div><span style="color: #94a3b8; font-size: 0.85rem;">P/E Ratio</span><br><span style="color: #f8fafc; font-weight: 500;">{pe_str}</span></div>
        <div><span style="color: #94a3b8; font-size: 0.85rem;">Market Cap</span><br><span style="color: #f8fafc; font-weight: 500;">{mc_str}</span></div>
    </div>
</div>
<!-- Debug: {s_info.get('debug', '')} -->
</div>
""", unsafe_allow_html=True)
