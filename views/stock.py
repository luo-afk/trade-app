import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from utils.ui_components import render_top_bar

st.session_state["current_page"] = "stock"
render_top_bar()

if "selected_ticker" not in st.session_state:
    st.info("Search for a stock to view details.")
    st.stop()

ticker = st.session_state["selected_ticker"]
stock = yf.Ticker(ticker)

# --- TIME CONTROLS ---
# We reuse the logic from the dashboard for consistency
if "stock_period" not in st.session_state:
    st.session_state["stock_period"] = "1D"

TIME_MAP = {
    "1D": ("1d", "5m"),
    "1W": ("5d", "15m"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "1Y": ("1y", "1d"),
    "ALL": ("max", "1w"),
}

c1, c2 = st.columns([2, 1])
with c1:
    st.title(ticker)
    # Simple Sector Badge
    try:
        info = stock.info
        st.caption(f"{info.get('longName', ticker)} • {info.get('sector', 'ETF/Crypto')}")
    except:
        st.caption("Asset Details")

with c2:
    # Time Buttons
    cols = st.columns(len(TIME_MAP))
    for i, label in enumerate(TIME_MAP.keys()):
        type = "primary" if st.session_state["stock_period"] == label else "secondary"
        if cols[i].button(label, key=f"btn_{label}", type=type, use_container_width=True):
            st.session_state["stock_period"] = label
            st.rerun()

# --- DATA ---
period, interval = TIME_MAP[st.session_state["stock_period"]]
hist = stock.history(period=period, interval=interval)

if hist.empty:
    st.warning("No data available.")
    st.stop()

# --- METRICS ---
curr = hist['Close'].iloc[-1]
start_val = hist['Close'].iloc[0]
diff = curr - start_val
pct = (diff / start_val) * 100

color = "#00FF00" if diff >= 0 else "#FF4B4B"

st.markdown(f"""
    <div style="font-size: 48px; font-weight: bold; font-family: sans-serif;">${curr:,.2f}</div>
    <div style="font-size: 18px; color: {color}; margin-bottom: 20px;">
        {'+' if diff >= 0 else ''}${diff:,.2f} ({pct:.2f}%) <span style="color: #666; font-size: 14px;">{st.session_state['stock_period']}</span>
    </div>
""", unsafe_allow_html=True)

# --- CHART ---
fig = go.Figure()

# Main Line
fig.add_trace(go.Scatter(
    x=hist.index, 
    y=hist['Close'],
    mode='lines',
    line=dict(color=color, width=2),
    fill='tozeroy',
    fillcolor=f"rgba({0 if diff < 0 else 0}, {255 if diff >= 0 else 0}, 0, 0.1)", # Green or Red tint
    hovertemplate='$%{y:,.2f}'
))

# Baseline Dotted
fig.add_trace(go.Scatter(
    x=[hist.index[0], hist.index[-1]],
    y=[start_val, start_val],
    mode='lines',
    line=dict(color="gray", width=1, dash='dot'),
    hoverinfo="skip"
))

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0,r=0,t=10,b=0),
    showlegend=False,
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- STATS CARDS ---
st.divider()
st.subheader("About")
col1, col2, col3, col4 = st.columns(4)

try:
    mcap = info.get('marketCap', 0)
    pe = info.get('trailingPE', '-')
    vol = info.get('averageVolume', 0)
    high = info.get('fiftyTwoWeekHigh', 0)

    # Helper to format big numbers
    def fmt_num(n):
        if n > 1e12: return f"{n/1e12:.2f}T"
        if n > 1e9: return f"{n/1e9:.2f}B"
        if n > 1e6: return f"{n/1e6:.2f}M"
        return str(n)

    col1.metric("Market Cap", fmt_num(mcap))
    col2.metric("P/E Ratio", pe)
    col3.metric("Avg Volume", fmt_num(vol))
    col4.metric("52W High", f"${high}")
    
    st.write(info.get('longBusinessSummary', ''))
except:
    st.caption("Detailed stats unavailable.")
