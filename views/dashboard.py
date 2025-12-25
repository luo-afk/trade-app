import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.db import get_trades, get_users
from utils.analytics import get_portfolio_history, get_benchmark_history

# --- CONFIG ---
# Default to 1 Day view automatically
if "dashboard_period" not in st.session_state:
    st.session_state["dashboard_period"] = "1d"

# Map readable periods to (yfinance_period, yfinance_interval)
TIME_MAP = {
    "1d":  ("1d", "5m"),
    "1w":  ("5d", "15m"),
    "1m":  ("1mo", "1d"),
    "3m":  ("3mo", "1d"),
    "1y":  ("1y", "1d"),
    "All": ("max", "1w"),
}

st.title("📊 Portfolio Performance")

# --- CONTROLS (Top Bar) ---
# Create a row of buttons for time selection like Public/Robinhood
c1, c2 = st.columns([2, 1])
with c1:
    # Use pills or segmented control if available, otherwise radio
    # Using columns for buttons to simulate a toolbar
    cols = st.columns(len(TIME_MAP))
    for i, label in enumerate(TIME_MAP.keys()):
        if cols[i].button(label, use_container_width=True):
            st.session_state["dashboard_period"] = label

with c2:
    # Comparison Logic
    all_users = get_users()
    user_options = [f"User: {u['username']}" for u in all_users if u['username'] != st.session_state["user"]["username"]]
    compare_options = ["SPY", "QQQ", "BTC-USD"] + user_options
    selected_benchmarks = st.multiselect("Compare:", compare_options, default=[], label_visibility="collapsed", placeholder="Compare...")

st.divider()

# --- DATA LOADING ---
selected_period, selected_interval = TIME_MAP[st.session_state["dashboard_period"]]

all_trades = pd.DataFrame(get_trades())
if all_trades.empty:
    st.info("No trades found. Log a trade to see your chart!")
    st.stop()

my_trades = all_trades[all_trades['user_name'] == st.session_state["user"]["username"]]

# Fetch History
with st.spinner(f"Loading {st.session_state['dashboard_period']} chart..."):
    my_history = get_portfolio_history(my_trades, period=selected_period, interval=selected_interval)

if my_history.empty:
    st.warning("Not enough data for this time period yet.")
    st.stop()

# --- METRICS HEADER ---
latest = my_history.iloc[-1]
start = my_history.iloc[0]

curr_val = latest["Portfolio Value"]
start_val = start["Portfolio Value"]
diff_val = curr_val - start_val
diff_pct = ((curr_val - start_val) / start_val) * 100 if start_val > 0 else 0

# Color logic
color_hex = "#00FF7F" if diff_val >= 0 else "#FF4B4B"

# Display Big Number
st.markdown(f"""
    <div style="font-size: 48px; font-weight: bold; margin-bottom: -10px;">${curr_val:,.2f}</div>
    <div style="font-size: 18px; color: {color_hex}; margin-bottom: 20px;">
        {'+' if diff_val > 0 else ''}${diff_val:,.2f} ({diff_val/start_val*100:.2f}%)
    </div>
""", unsafe_allow_html=True)

# --- THE CHART ---

# LOGIC SWITCH: 
# If NO comparison -> Show Dollar Value (Clean, filled area)
# If YES comparison -> Show % Return (Lines only, for fairness)
is_comparison_mode = len(selected_benchmarks) > 0

fig = go.Figure()

# 1. Add User Line
if is_comparison_mode:
    # Percent View
    fig.add_trace(go.Scatter(
        x=my_history["Date"], 
        y=my_history["Return %"],
        mode='lines',
        name='My Portfolio',
        line=dict(color=color_hex, width=2),
        hovertemplate='%{y:.2f}%'
    ))
else:
    # Dollar View (Public style)
    fig.add_trace(go.Scatter(
        x=my_history["Date"], 
        y=my_history["Portfolio Value"],
        mode='lines',
        name='My Portfolio',
        line=dict(color=color_hex, width=2),
        fill='tozeroy', # Fill area under line
        fillcolor=f"rgba({0 if diff_val < 0 else 0}, {255 if diff_val >= 0 else 75}, {127 if diff_val >= 0 else 75}, 0.1)",
        hovertemplate='$%{y:,.2f}<br>Return: %{customdata:.2f}%',
        customdata=my_history["Return %"] # Pass return % to tooltip
    ))

# 2. Add Comparisons
for bench in selected_benchmarks:
    # Note: Comparisons are ALWAYS % return because comparing $500 SPY to $2000 Portfolio on a dollar axis is messy
    if "User: " in bench:
        target_user = bench.replace("User: ", "")
        their_trades = all_trades[all_trades['user_name'] == target_user]
        their_hist = get_portfolio_history(their_trades, period=selected_period, interval=selected_interval)
        if not their_hist.empty:
            fig.add_trace(go.Scatter(
                x=their_hist["Date"], y=their_hist["Return %"],
                mode='lines', name=target_user
            ))
    else:
        bench_hist = get_benchmark_history(bench, period=selected_period, interval=selected_interval)
        if not bench_hist.empty:
            fig.add_trace(go.Scatter(
                x=bench_hist["Date"], y=bench_hist["Return %"],
                mode='lines', name=bench, line=dict(dash='dot')
            ))

# 3. Public.com Styling (Minimalist)
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=is_comparison_mode, # Only show legend if comparing
    hovermode="x unified",
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False # Hide dates on X axis for cleaner look? Or True if you prefer.
    ),
    yaxis=dict(
        showgrid=False, # Hide grid lines
        zeroline=False,
        showticklabels=is_comparison_mode, # Hide Y axis dollar amounts (since big number is at top)
        tickprefix="$" if not is_comparison_mode else "",
        ticksuffix="%" if is_comparison_mode else ""
    )
)

# Hide the modebar (zoom buttons)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})
