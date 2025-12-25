import streamlit as st
import datetime
import pytz
import yfinance as yf

# --- CACHED DATA FETCH ---
@st.cache_data(ttl=60) # Updates every minute
def get_market_tape():
    """Fetches live data for the top bar strip"""
    tickers = ["SPY", "QQQ", "BTC-USD", "^VIX"]
    try:
        data = yf.download(tickers, period="5d", interval="1d", progress=False)['Close']
        tape_data = []
        for t in tickers:
            if len(data) >= 2:
                # Handle potential MultiIndex columns or flat columns
                try:
                    series = data[t] if isinstance(data.columns, pd.MultiIndex) else data[t]
                except:
                    # Fallback if structure varies
                    series = data.iloc[:, tickers.index(t)]
                
                curr = series.iloc[-1]
                prev = series.iloc[-2]
                pct = ((curr - prev) / prev) * 100
                
                # Clean names
                name = t.replace("-USD", "").replace("^", "")
                tape_data.append({"name": name, "price": curr, "pct": pct})
        return tape_data
    except:
        return []

def get_market_status():
    tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(tz)
    is_weekday = now.weekday() < 5
    current_hour = now.hour + (now.minute / 60)
    is_open = is_weekday and (9.5 <= current_hour < 16.0)
    
    status_text = "Market Open" if is_open else "Market Closed"
    date_str = now.strftime("%B %d")
    return status_text, date_str

def render_top_bar():
    # Load CSS
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # 1. Top Row: Search & Status
    c1, c2 = st.columns([1, 3], gap="medium")
    
    with c1:
        # Search Bar
        def handle_search():
            if st.session_state["top_search"]:
                st.session_state["selected_ticker"] = st.session_state["top_search"].upper()
                st.session_state["top_search"] = ""
                st.session_state["trigger_redirect"] = True

        st.text_input(
            "Search", key="top_search", 
            placeholder="Search assets...", 
            label_visibility="collapsed", 
            on_change=handle_search
        )
        
        if st.session_state.get("trigger_redirect"):
            st.session_state["trigger_redirect"] = False
            st.switch_page("views/stock.py")

    with c2:
        # Market Status Text (Small, aligned)
        status, date = get_market_status()
        st.markdown(f"""
            <div style="display: flex; align-items: center; height: 42px; color: #666; font-size: 13px;">
                <span>{status} &nbsp; • &nbsp; {date}</span>
            </div>
        """, unsafe_allow_html=True)

    # 2. Market Strip (The "Public" Look)
    tape = get_market_tape()
    if tape:
        html_items = ""
        for item in tape:
            color = "#00FF00" if item['pct'] >= 0 else "#FF4B4B"
            arrow = "↗" if item['pct'] >= 0 else "↘"
            html_items += f"""
                <div class="ticker-item">
                    <span class="ticker-symbol">{item['name']}</span>
                    <span style="color: {color};">${item['price']:,.2f}</span>
                    <span style="color: {color}; font-size: 11px;">{arrow} {abs(item['pct']):.2f}%</span>
                </div>
                <div style="width: 1px; height: 12px; background: #333;"></div>
            """
        
        st.markdown(f"""
            <div class="ticker-tape">
                <div style="color: #666; font-weight: bold; margin-right: 10px;">Summary ⌄</div>
                {html_items}
            </div>
        """, unsafe_allow_html=True)
