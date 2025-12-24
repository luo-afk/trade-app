import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_trades, get_users
from utils.analytics import get_portfolio_history, get_benchmark_history

st.title("📊 Portfolio Performance")

# --- CONTROLS ---
col_ctrl1, col_ctrl2 = st.columns([1, 2])

with col_ctrl1:
    # Default to "1d" (Index 0)
    time_period = st.selectbox("Time Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd"], index=0)

with col_ctrl2:
    # Universal Comparison Logic
    all_users = get_users()
    user_options = [f"User: {u['username']}" for u in all_users if u['username'] != st.session_state["user"]["username"]]
    
    # Default list + Users
    predefined = ["SPY", "QQQ", "BTC-USD"] + user_options
    
    # The Multiselect (Empty by default)
    selected_benchmarks = st.multiselect("Compare with:", predefined, default=[])
    
    # Custom Ticker Input
    custom_compare = st.text_input("Or type any ticker to compare (e.g. GME, AMD)", placeholder="Type ticker and press Enter")
    
    if custom_compare:
        selected_benchmarks.append(custom_compare.upper())

st.divider()

# --- DATA LOADING ---
all_trades = pd.DataFrame(get_trades())
if all_trades.empty:
    st.info("No trades found.")
    st.stop()

my_trades = all_trades[all_trades['user_name'] == st.session_state["user"]["username"]]

# Generate History
my_history = get_portfolio_history(my_trades, period=time_period)

if my_history.empty:
    st.warning("Not enough data to chart.")
    st.stop()

# --- THE CHART ---
latest = my_history.iloc[-1]
current_val = latest["Portfolio Value"]
current_return = latest["Return %"]

m1, m2, m3 = st.columns(3)
m1.metric("Portfolio Value", f"${current_val:,.2f}")
m2.metric("Total Return", f"{current_return:.2f}%", delta=f"{current_return:.2f}%")
m3.caption(f"Period: {time_period.upper()}")

# Prepare Chart Data
chart_df = my_history[["Date", "Return %"]].copy()
chart_df["Type"] = "My Portfolio"

# Add Benchmarks
for bench in selected_benchmarks:
    if "User: " in bench:
        target_user = bench.replace("User: ", "")
        their_trades = all_trades[all_trades['user_name'] == target_user]
        if not their_trades.empty:
            their_hist = get_portfolio_history(their_trades, period=time_period)
            if not their_hist.empty:
                temp_df = their_hist[["Date", "Return %"]].copy()
                temp_df["Type"] = target_user
                chart_df = pd.concat([chart_df, temp_df])
    else:
        # Comparison to ANY ticker
        bench_hist = get_benchmark_history(bench, period=time_period)
        if not bench_hist.empty:
            bench_hist["Type"] = bench
            chart_df = pd.concat([chart_df, bench_hist])

# Plot
fig = px.line(
    chart_df, 
    x="Date", 
    y="Return %", 
    color="Type", 
    template="plotly_dark",
    color_discrete_map={"My Portfolio": "#00FF7F"}
)

fig.update_traces(selector={"name": "My Portfolio"}, fill='tozeroy', fillcolor='rgba(0, 255, 127, 0.1)')
fig.update_yaxes(ticksuffix="%")

st.plotly_chart(fig, use_container_width=True)
