import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db import get_trades, get_users
from utils.analytics import get_portfolio_history, get_benchmark_history
from utils.ui_components import render_top_bar

st.session_state["current_page"] = "compare"
render_top_bar()

st.title("⚖️ Compare Performance")

# --- CONTROLS ---
c1, c2 = st.columns(2)
with c1:
    period = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y", "ytd", "max"], index=3)
with c2:
    # Users + Benchmarks
    users = get_users()
    user_opts = [f"User: {u['username']}" for u in users]
    defaults = ["SPY", "QQQ"] + user_opts
    
    # Default to current user and SPY
    current_username = st.session_state['user']['username']
    default_selection = ["SPY", f"User: {current_username}"]
    
    targets = st.multiselect("Add to Chart", defaults, default=default_selection)

if not targets:
    st.info("Select assets or users to compare.")
    st.stop()

# --- FETCH DATA ---
df_chart = pd.DataFrame()
all_trades = pd.DataFrame(get_trades())

with st.spinner("Analyzing..."):
    for t in targets:
        temp_df = pd.DataFrame()
        
        if "User: " in t:
            # User History
            uname = t.replace("User: ", "")
            u_trades = all_trades[all_trades['user_name'] == uname]
            if not u_trades.empty:
                hist = get_portfolio_history(u_trades, period=period, interval="1d") # Use 1d for long comparisons
                if not hist.empty:
                    temp_df = hist[["Date", "Return %"]].copy()
                    temp_df["Name"] = uname
        else:
            # Ticker History
            hist = get_benchmark_history(t, period=period, interval="1d")
            if not hist.empty:
                temp_df = hist[["Date", "Return %"]].copy()
                temp_df["Name"] = t
        
        if not temp_df.empty:
            df_chart = pd.concat([df_chart, temp_df])

# --- RENDER CHART ---
if not df_chart.empty:
    fig = px.line(
        df_chart, 
        x="Date", y="Return %", color="Name",
        template="plotly_dark",
        color_discrete_map={
            st.session_state['user']['username']: "#00C805", # My line is green
            "SPY": "#888"
        }
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#222")
    )
    fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data found for selected targets.")
