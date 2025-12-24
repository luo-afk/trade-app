import streamlit as st
import pandas as pd
from utils.db import get_trades, get_users
from utils.analytics import get_portfolio_history, get_bulk_history

st.title("🏆 Market Leaderboard")

st.write("Ranking Family Portfolios against major ETFs.")

# 1. Controls
period = st.select_slider("Ranking Period", options=["5d", "1mo", "3mo", "6mo", "1y", "ytd"], value="1mo")

# 2. Data Gathering
ranking_data = []

with st.spinner(f"Analyzing market data for {period}..."):
    
    # A. Get Users Performance
    all_trades = pd.DataFrame(get_trades())
    all_users = get_users()
    
    for u in all_users:
        username = u['username']
        u_trades = all_trades[all_trades['user_name'] == username]
        
        if not u_trades.empty:
            # We use get_portfolio_history to get accurate User ROI
            hist = get_portfolio_history(u_trades, period=period)
            if not hist.empty:
                last_day = hist.iloc[-1]
                ranking_data.append({
                    "Name": u['full_name'],
                    "Type": "User",
                    "Return %": last_day["Return %"]
                })

    # B. Get ETF Performance
    etfs = ["SPY", "QQQ", "VOO", "VGT", "SCHD", "IWM", "DIA"]
    etf_data = get_bulk_history(etfs, period=period)
    
    if not etf_data.empty:
        for _, row in etf_data.iterrows():
            ranking_data.append({
                "Name": row['Name'],
                "Type": "ETF",
                "Return %": row['Return %']
            })

# 3. Display
if ranking_data:
    df = pd.DataFrame(ranking_data).sort_values("Return %", ascending=False).reset_index(drop=True)
    
    # Add Rank Column
    df.index = df.index + 1
    df.index.name = "Rank"
    
    # Styling function to highlight Users vs ETFs
    def highlight_type(val):
        color = '#00FF7F' if val == 'User' else '#A0A0A0'
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df,
        column_config={
            "Return %": st.column_config.NumberColumn(format="%.2f%%")
        },
        use_container_width=True
    )
    
    # Quick Winner Announcement
    winner = df.iloc[0]
    st.markdown(f"### 🥇 The Winner is **{winner['Name']}** with a **{winner['Return %']:.2f}%** return!")
    
else:
    st.warning("Not enough data to calculate rankings yet.")
