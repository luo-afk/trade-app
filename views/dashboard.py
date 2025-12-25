import streamlit as st
import plotly.graph_objects as go
from utils.db import get_trades
from utils.analytics import get_portfolio_history, get_benchmark_history
from utils.ui_components import render_top_bar

# 1. Render Top Bar
render_top_bar()

# --- CONFIG ---
# FIX: Ensure default is uppercase '1D' to match the TIME_MAP keys
if "dashboard_period" not in st.session_state:
    st.session_state["dashboard_period"] = "1D"

# Map to (period, interval)
TIME_MAP = {
    "1D": ("1d", "5m"),
    "1W": ("5d", "15m"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "1Y": ("1y", "1d"),
    "ALL": ("max", "1w"),
}

# Safety check: If session state has an invalid old key (like '1d' lowercase), reset it
if st.session_state["dashboard_period"] not in TIME_MAP:
    st.session_state["dashboard_period"] = "1D"

# --- CONTROLS ---
# Simple segmented text buttons for time
cols = st.columns(len(TIME_MAP))
for i, label in enumerate(TIME_MAP.keys()):
    # Highlight the selected one
    type = "primary" if st.session_state["dashboard_period"] == label else "secondary"
    if cols[i].button(label, key=label, type=type, use_container_width=True):
        st.session_state["dashboard_period"] = label
        st.rerun()

# --- DATA ---
selected_period, selected_interval = TIME_MAP[st.session_state["dashboard_period"]]
all_trades = get_trades()

if not all_trades:
    st.info("No trades yet.")
    st.stop()

# Filter my trades
import pandas as pd
df_trades = pd.DataFrame(all_trades)
my_trades = df_trades[df_trades['user_name'] == st.session_state["user"]["username"]]

# Get History
with st.spinner("Loading..."):
    history = get_portfolio_history(my_trades, period=selected_period, interval=selected_interval)

if history.empty:
    st.warning("Market data unavailable for this period (or market is closed).")
    st.stop()

# --- METRICS & BASELINE ---
latest = history.iloc[-1]
# Baseline is the first point of the chart
baseline_value = history.iloc[0]["Portfolio Value"]
current_value = latest["Portfolio Value"]

diff = current_value - baseline_value
pct = (diff / baseline_value) * 100 if baseline_value > 0 else 0

# Color Logic: Green if ABOVE baseline, Red if BELOW
line_color = "#00FF7F" if diff >= 0 else "#FF4B4B"

# Big Number
st.markdown(f"""
    <div style="font-size: 42px; font-weight: 700;">${current_value:,.2f}</div>
    <div style="color: {line_color}; font-size: 16px; margin-bottom: 20px;">
        {'+' if diff >= 0 else ''}${diff:,.2f} ({pct:.2f}%)
    </div>
""", unsafe_allow_html=True)

# --- CHART ---
fig = go.Figure()

# 1. The Portfolio Line
fig.add_trace(go.Scatter(
    x=history["Date"], 
    y=history["Portfolio Value"],
    mode='lines',
    line=dict(color=line_color, width=2),
    name="Portfolio",
    hovertemplate='$%{y:,.2f}'
))

# 2. The Baseline (Dotted Line)
fig.add_trace(go.Scatter(
    x=[history["Date"].iloc[0], history["Date"].iloc[-1]],
    y=[baseline_value, baseline_value],
    mode='lines',
    line=dict(color="gray", width=1, dash='dot'),
    name="Open",
    hoverinfo="skip"
))

# 3. Styling
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=False,
    hovermode="x unified",
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)  
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
