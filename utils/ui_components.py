import streamlit as st
import datetime
import pytz
import yfinance as yf
import pandas as pd

@st.cache_data(ttl=60)
def get_market_tape():
    symbols = {"SPY": "SPY", "QQQ": "QQQ", "BTC-USD": "BTC", "^VIX": "VIX"}
    tickers = list(symbols.keys())
    try:
        data = yf.download(tickers, period="5d", interval="1d", progress=False)['Close']
        tape_data = []
        for t in tickers:
            series = None
            if t in data.columns:
                series = data[t]
            
            if series is not None:
                series = series.dropna()
                if len(series) >= 2:
                    curr = series.iloc[-1]
                    prev = series.iloc[-2]
                    pct = ((curr - prev) / prev) * 100
                    tape_data.append({"name": symbols[t], "price": curr, "pct": pct})
        return tape_data
    except:
        return []

def get_market_status():
    tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(tz)
    is_weekday = now.weekday() < 5
    current_hour = now.hour + (now.minute / 60)
    is_open = is_weekday and (9.5 <= current_hour < 16.0)
    
    color = "#00FF00" if is_open else "#888888"
    status_text = "Market Open" if is_open else "Market Closed"
    date_str = now.strftime("%B %d")
    return color, status_text, date_str

def render_top_bar():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # 1. TOP ROW: Search (Left) | Status (Right)
    c1, c2 = st.columns([1, 1], gap="medium", vertical_alignment="center")
    
    with c1:
        def handle_search():
            if st.session_state["top_search"]:
                st.session_state["selected_ticker"] = st.session_state["top_search"].upper()
                st.session_state["top_search"] = ""
                st.session_state["trigger_redirect"] = True

        st.text_input(
            "Search", key="top_search", 
            placeholder="Search assets (e.g. NVDA)...", 
            label_visibility="collapsed", 
            on_change=handle_search
        )
        
        if st.session_state.get("trigger_redirect"):
            st.session_state["trigger_redirect"] = False
            st.switch_page("views/stock.py")

    with c2:
        color, status, date = get_market_status()
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; color: #666; font-size: 13px; font-family: sans-serif;">
                <span style="color: {color}; font-weight: bold; margin-right: 8px;">● {status.upper()}</span>
                <span>{date}</span>
            </div>
        """, unsafe_allow_html=True)

    # 2. MARKET TAPE
    tape = get_market_tape()
    if tape:
        html_items = ""
        for item in tape:
            color = "#00FF00" if item['pct'] >= 0 else "#FF4B4B"
            arrow = "↗" if item['pct'] >= 0 else "↘"
            
            html_items += f"""<div class="ticker-item">
<span style="font-weight:700; color:#DDD;">{item['name']}</span>
<span style="color:{color};">${item['price']:,.2f}</span>
<span style="color:{color}; font-size:11px;">{arrow} {abs(item['pct']):.2f}%</span>
</div>
<div style="width:1px; height:12px; background:#333;"></div>"""
        
        st.markdown(f"""
<div class="ticker-tape">
<span style="color:#666; font-weight:bold; font-size:12px; margin-right:10px;">Summary</span>
<div style="width:1px; height:12px; background:#333;"></div>
{html_items}
</div>
""", unsafe_allow_html=True)
