import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_trades, get_users
from utils.analytics import get_portfolio_history, get_benchmark_history

st.title("📊 Portfolio Performance")

# --- 1. CONTROLS (Time & Comparison) ---
col_ctrl1, col_ctrl2 = st.columns([1, 2])

with col_ctrl1:
    # Time Period Selector
    time_period = st.selectbox("Time Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd"], index=2)

with col_ctrl2:
    # Benchmark / User Comparison
    # Get other users
    all_users = get_users()
    user_options = [u['username'] for u in all_users if u['username'] != st.session_state["user"]["username"]]
    
    compare_options = ["SPY", "QQQ", "BTC-USD"] + [f"User: {u}" for u in user_options]
    
    benchmarks = st.multiselect("Compare with:", compare_options, default=["SPY"])

st.divider()

# --- 2. DATA PREPARATION ---
# Get current user trades
all_trades = pd.DataFrame(get_trades())
if all_trades.empty:
    st.info("No trades found. Log a trade to see the chart.")
    st.stop()

# Filter for current user
my_trades = all_trades[all_trades['user_name'] == st.session_state["user"]["username"]]

# Generate History for Current User
with st.spinner("Crunching numbers..."):
    my_history = get_portfolio_history(my_trades, period=time_period)

if my_history.empty:
    st.warning("Not enough data to chart this time period.")
    st.stop()

# --- 3. THE BIG CHART ---

# Get the latest values for the big number display
latest = my_history.iloc[-1]
current_val = latest["Portfolio Value"]
current_return = latest["Return %"]

# Metrics Row
m1, m2, m3 = st.columns(3)
m1.metric("Portfolio Value", f"${current_val:,.2f}")
m2.metric("Total Return", f"{current_return:.2f}%", delta=f"{current_return:.2f}%")
m3.caption(f"Showing data for: {time_period.upper()}")

# Prepare Chart Data
# We start with our data
chart_df = my_history[["Date", "Return %"]].copy()
chart_df["Type"] = "My Portfolio"

# Add Benchmarks (SPY, etc.)
for bench in benchmarks:
    if "User: " in bench:
        # Compare against another user
        target_user = bench.replace("User: ", "")
        their_trades = all_trades[all_trades['user_name'] == target_user]
        if not their_trades.empty:
            their_hist = get_portfolio_history(their_trades, period=time_period)
            if not their_hist.empty:
                temp_df = their_hist[["Date", "Return %"]].copy()
                temp_df["Type"] = target_user # Label as their name
                chart_df = pd.concat([chart_df, temp_df])
    else:
        # Compare against Ticker (SPY, BTC)
        bench_hist = get_benchmark_history(bench, period=time_period)
        if not bench_hist.empty:
            bench_hist["Type"] = bench
            chart_df = pd.concat([chart_df, bench_hist])

# Plotly Line Chart
fig = px.line(
    chart_df, 
    x="Date", 
    y="Return %", 
    color="Type", 
    title=f"Growth Comparison ({time_period})",
    template="plotly_dark", # Matches the dark theme
    color_discrete_map={
        "My Portfolio": "#00FF7F", # Bright Green for user
        "SPY": "gray",
        "BTC-USD": "orange"
    }
)

# Make it look like the Public app (Fill area for user only)
# This is a bit advanced plotly config
fig.update_traces(selector={"name": "My Portfolio"}, fill='tozeroy', fillcolor='rgba(0, 255, 127, 0.1)')
fig.update_yaxes(ticksuffix="%")
st.plotly_chart(fig, use_container_width=True)


# --- 4. ROI LEADERBOARD ---
st.subheader("🏆 Growth Leaderboard")

# Calculate ROI for every user found in trades
if not all_trades.empty:
    users_in_trades = all_trades['user_name'].unique()
    leaderboard_data = []

    for u in users_in_trades:
        u_trades = all_trades[all_trades['user_name'] == u]
        # Get history to calculate accurate ROI based on holding duration
        # Or simpler: (Current Value - Cost Basis) / Cost Basis
        # We re-use the history function for accuracy
        hist = get_portfolio_history(u_trades, period="1y") # Look at 1Y for leaderboard
        if not hist.empty:
            last_day = hist.iloc[-1]
            leaderboard_data.append({
                "Trader": u,
                "Return %": last_day["Return %"],
                "Portfolio Value": last_day["Portfolio Value"]
            })

    lb_df = pd.DataFrame(leaderboard_data).sort_values("Return %", ascending=False)
    
    # Display nicely
    st.dataframe(
        lb_df,
        column_order=["Trader", "Return %", "Portfolio Value"],
        column_config={
            "Return %": st.column_config.NumberColumn(format="%.2f%%"),
            "Portfolio Value": st.column_config.NumberColumn(format="$%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )
