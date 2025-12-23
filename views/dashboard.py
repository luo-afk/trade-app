import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from utils.db import get_trades
from utils.market import calculate_portfolio_value

st.title("📊 Performance Overview")

# 1. Load User Data
raw_data = get_trades()
df = pd.DataFrame(raw_data)

if df.empty:
    st.warning("No data yet. Go to 'Log a Trade' to start.")
    st.stop()

# 2. Calculate Portfolio Values
total_val, enriched_df = calculate_portfolio_value(df)

# 3. Get Benchmark Data (S&P 500)
# We fetch SPY history to compare 
@st.cache_data
def get_benchmark():
    spy = yf.Ticker("SPY")
    hist = spy.history(period="1mo")
    # Calculate % return over last month
    start = hist['Close'].iloc[0]
    end = hist['Close'].iloc[-1]
    return ((end - start) / start) * 100

spy_return = get_benchmark()

# 4. Calculate User Return (Simple approximation for now)
# (Current Value - Total Cost) / Total Cost
total_cost = enriched_df['cost_basis'].sum()
user_pnl = total_val - total_cost
user_return = (user_pnl / total_cost) * 100 if total_cost > 0 else 0

# 5. The Comparison Section
st.subheader("Family vs. The Market (1 Mo)")

col1, col2, col3 = st.columns(3)
col1.metric("Family Portfolio Return", f"{user_return:.2f}%", delta=f"{user_return:.2f}%")
col2.metric("S&P 500 (Benchmark)", f"{spy_return:.2f}%", delta=f"{spy_return:.2f}%", delta_color="off")
col3.metric("Alpha (Beating the Market)", f"{user_return - spy_return:.2f}%", 
            delta_color="normal" if user_return > spy_return else "inverse")

st.markdown("---")

# 6. Leaderboard (Who is doing best?)
st.subheader("🏆 Family Leaderboard")
if 'return_pct' in enriched_df.columns:
    # Group by user and avg return
    leaderboard = enriched_df.groupby('user_name')['unrealized_pnl'].sum().reset_index()
    leaderboard = leaderboard.sort_values('unrealized_pnl', ascending=False)
    
    st.dataframe(
        leaderboard, 
        column_config={
            "user_name": "Trader",
            "unrealized_pnl": st.column_config.NumberColumn("Total Profit", format="$%.2f")
        },
        hide_index=True,
        use_container_width=True
    )
