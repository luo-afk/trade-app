import streamlit as st
import plotly.graph_objects as go
from utils.db import get_trades
from utils.analytics import get_portfolio_history
from utils.ui_components import render_top_bar
import pandas as pd

st.session_state["current_page"] = "dashboard"
render_top_bar()

# --- CONFIG ---
if "dashboard_period" not in st.session_state:
    st.session_state["dashboard_period"] = "1D"

TIME_MAP = {
    "1D": ("1d", "5m"), "1W": ("5d", "15m"), "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"), "1Y": ("1y", "1d"), "ALL": ("max", "1w"),
}

# --- DATA ---
all_trades = get_trades()
if not all_trades:
    st.info("No trades yet.")
    st.stop()

df_trades = pd.DataFrame(all_trades)
my_trades = df_trades[df_trades['user_name'] == st.session_state["user"]["username"]]

selected_period, selected_interval = TIME_MAP[st.session_state["dashboard_period"]]

with st.spinner(""):
    history = get_portfolio_history(my_trades, period=selected_period, interval=selected_interval)

if history.empty:
    st.warning("Market Closed / No Data")
    st.stop()

# --- HEADER LAYOUT ---
latest = history.iloc[-1]
baseline_value = history.iloc[0]["Portfolio Value"]
current_value = latest["Portfolio Value"]

diff = current_value - baseline_value
pct = (diff / baseline_value) * 100 if baseline_value > 0 else 0
line_color = "#00FF00" if diff >= 0 else "#FF4B4B"

# ADJUSTED COLUMN RATIO: [1, 1] to give buttons more room
c1, c2 = st.columns([1, 1], vertical_alignment="bottom")

with c1:
    st.markdown(f"""
        <div style="font-size: 36px; font-weight: 700; line-height: 1;">${current_value:,.2f}</div>
        <div style="color: {line_color}; font-size: 14px;">
            {'+' if diff >= 0 else ''}${diff:,.2f} ({pct:.2f}%) 
            <span style="color:#666; margin-left:5px;">{st.session_state["dashboard_period"]}</span>
        </div>
    """, unsafe_allow_html=True)

with c2:
    # Use gap="small" to keep them together, but rely on CSS for width
    b_cols = st.columns(len(TIME_MAP), gap="small")
    for i, label in enumerate(TIME_MAP.keys()):
        is_active = st.session_state["dashboard_period"] == label
        kind = "primary" if is_active else "secondary"
        # We assume CSS will handle the squishing now
        if b_cols[i].button(label, key=label, type=kind, use_container_width=True):
            st.session_state["dashboard_period"] = label
            st.rerun()

# --- CHART ---
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=history["Date"], 
    y=history["Portfolio Value"],
    mode='lines',
    line=dict(color=line_color, width=2),
    fill='tozeroy',
    fillcolor=f"rgba({0 if diff < 0 else 0}, {255 if diff >= 0 else 0}, 0, 0.1)",
    name="Portfolio",
    hovertemplate='$%{y:,.2f}'
))

fig.add_trace(go.Scatter(
    x=[history["Date"].iloc[0], history["Date"].iloc[-1]],
    y=[baseline_value, baseline_value],
    mode='lines',
    line=dict(color="#444", width=1, dash='dot'),
    hoverinfo="skip"
))

y_min = history["Portfolio Value"].min()
y_max = history["Portfolio Value"].max()
padding = (y_max - y_min) * 0.1 if y_max != y_min else y_max * 0.01
range_y = [y_min - padding, y_max + padding]

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=10, b=0),
    height=300,
    showlegend=False,
    hovermode="x unified",
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=range_y)  
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
