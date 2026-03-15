import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go
import numpy as np

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
                # Need specific start and end to get 1 year range securely
                data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                tkr = yf.Ticker(ticker)
                info = tkr.info
                
                if not data.empty:
                    # Fix multi-level columns if pandas>2 and yfinance structure changed
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                        
                    data['MA50'] = data['Close'].rolling(window=50).mean()
                    data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
                    
                    stock_data[ticker] = data
                    
                    # Store info
                    stock_info[ticker] = {
                        '52w_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                        '52w_low': info.get('fiftyTwoWeekLow', 'N/A'),
                        'pe': info.get('trailingPE', info.get('forwardPE', 'N/A')),
                        'market_cap': info.get('marketCap', 'N/A')
                    }
                    valid_tickers.append(ticker)
            except Exception as e:
                st.error(f"Error for {ticker}: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
                
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
                
                last_close = float(data['Close'].iloc[-1])
                
                ako_price = last_close * (ako_pct / 100.0)
                k_price = last_close * (k_pct / 100.0)
                eki_price = last_close * (eki_pct / 100.0)
                
                # Format metrics
                mc = s_info['market_cap']
                if isinstance(mc, (int, float)):
                    mc_str = f"${mc/1e9:.1f}B" if mc >= 1e9 else (f"${mc/1e6:.1f}M" if mc >= 1e6 else f"${mc}")
                else:
                    mc_str = "N/A"
                    
                pe_val = s_info['pe']
                pe_str = f"{pe_val:.2f}" if isinstance(pe_val, float) else pe_val
                
                high_val = s_info['52w_high']
                high_str = f"${high_val:.2f}" if isinstance(high_val, float) else high_val
                
                low_val = s_info['52w_low']
                low_str = f"${low_val:.2f}" if isinstance(low_val, float) else low_val

                # Build Plotly Chart
                fig = go.Figure()
                
                # Candlestick chart
                fig.add_trace(go.Candlestick(
                    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
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
                    xaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickfont=dict(size=10, color="#64748b")),
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

<div class="card-footer">
    <span>52W High: <span class="f-val">{high_str}</span></span>
    <span>52W Low: <span class="f-val">{low_str}</span></span>
    <span>P/E: <span class="f-val">{pe_str}</span></span>
    <span>市值: <span class="f-val">{mc_str}</span></span>
</div>
</div>
""", unsafe_allow_html=True)
