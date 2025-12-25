import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.db import get_trades, get_users
from utils.analytics import get_portfolio_history, get_benchmark_history
from utils.ui_components import render_top_bar

st.session_state["current_page"] = "compare"
render_top_bar()

st.title("⚖️ Compare Performance")

# --- CONTROLS ---
# Default Period: 1D (per request)
if "compare_period" not in st.session_state:
    st.session_state["compare_period"] = "1d"

c1, c2 = st.columns([1, 2])
with c1:
    period = st.selectbox("Timeframe", ["1d", "1mo", "3mo", "6mo", "1y", "ytd", "max"], index=0)

with c2:
    users = get_users()
    current_user = st.session_state['user']['username']
    
    # Default: Me vs SPY
    defaults = [f"User: {current_user}", "SPY"]
    
    options = ["SPY", "QQQ", "BTC-USD"] + [f"User: {u['username']}" for u in users]
    targets = st.multiselect("Assets / Users", options, default=defaults)

if not targets:
    st.stop()

# --- FETCH DATA ---
df_chart = pd.DataFrame()
all_trades = pd.DataFrame(get_trades())
chart_data = {} # Store traces

# Map 1d -> Intraday interval for better comparison
interval = "5m" if period in ["1d", "5d"] else "1d"

with st.spinner("Crunching numbers..."):
    for t in targets:
        temp_df = pd.DataFrame()
        
        if "User: " in t:
            uname = t.replace("User: ", "")
            u_trades = all_trades[all_trades['user_name'] == uname]
            if not u_trades.empty:
                hist = get_portfolio_history(u_trades, period=period, interval=interval)
                if not hist.empty:
                    chart_data[uname] = hist
        else:
            hist = get_benchmark_history(t, period=period, interval=interval)
            if not hist.empty:
                chart_data[t] = hist

# --- RENDER MODERN CHART ---
fig = go.Figure()

for name, data in chart_data.items():
    # Style logic: Me = Green, Others = Colors
    color = "#00FF00" if name == current_user else None
    
    fig.add_trace(go.Scatter(
        x=data["Date"],
        y=data["Return %"],
        mode='lines',
        name=name,
        line=dict(color=color, width=2)
    ))

# Add Baseline (0%)
fig.add_hline(y=0, line_dash="dot", line_color="#333", annotation_text="Baseline")

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    hovermode="x unified",
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#222", zeroline=False, ticksuffix="%"),
    legend=dict(orientation="h", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
