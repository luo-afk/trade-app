st.session_state["current_page"] = "stock"

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from utils.ui_components import render_top_bar

render_top_bar()

# Check if a ticker is selected
if "selected_ticker" not in st.session_state:
    st.info("Use the search bar above to find a stock.")
    st.stop()

ticker = st.session_state["selected_ticker"]

# Fetch Data
stock = yf.Ticker(ticker)
info = stock.info

# Layout
st.title(f"{info.get('shortName', ticker)}")
st.caption(f"{ticker} • {info.get('sector', 'Unknown Sector')}")

# Price Chart (Simple 1mo view)
hist = stock.history(period="1mo")
if not hist.empty:
    curr = hist['Close'].iloc[-1]
    prev = hist['Close'].iloc[0]
    color = "#00FF7F" if curr >= prev else "#FF4B4B"
    
    st.metric("Price", f"${curr:,.2f}", f"{(curr-prev)/prev*100:.2f}%")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color=color)))
    fig.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Stats Grid
st.subheader("Stats")
c1, c2, c3 = st.columns(3)
c1.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.2f}B")
c2.metric("P/E Ratio", info.get('trailingPE', '-'))
c3.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 0)}")

st.markdown(f"**Summary:** {info.get('longBusinessSummary', 'No summary available.')}")
