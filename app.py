import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import check_login
from utils.db import log_trade, get_trades
from utils.market import calculate_portfolio_value

# 1. Config & Login
st.set_page_config(page_title="Public Family", page_icon="📈", layout="wide") # 'Wide' layout looks more like a dashboard
user = check_login()

# 2. Sidebar (Profile)
with st.sidebar:
    st.header(f"👤 {user['full_name']}")
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
    st.markdown("---")
    st.write("### ➕ Add Trade")
    with st.form("add_trade"):
        t_ticker = st.text_input("Ticker").upper()
        t_action = st.selectbox("Action", ["Buy", "Sell"])
        t_qty = st.number_input("Shares", min_value=0.01, step=0.1) # NEW: Quantity
        t_price = st.number_input("Entry Price", min_value=0.01, step=0.01)
        t_reason = st.text_area("Thesis")
        if st.form_submit_button("Submit"):
            log_trade(user['username'], t_ticker, t_action, t_price, t_qty, t_reason)
            st.success("Trade Logged!")
            st.rerun()

# 3. Main Dashboard
st.title("Family Portfolio")

# Load Data
raw_data = get_trades()
df = pd.DataFrame(raw_data)

if not df.empty:
    # --- REAL TIME CALCULATIONS ---
    # Only calculate for OPEN positions (assuming everything logged is held for now)
    # For a complex app, you'd filter out 'Closed' trades.
    total_val, enriched_df = calculate_portfolio_value(df)
    
    total_invested = enriched_df['cost_basis'].sum()
    total_pnl = total_val - total_invested
    pnl_color = "normal" if total_pnl >= 0 else "off" # Streamlit metric delta color handling

    # --- TOP METRICS ROW ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Portfolio Value", f"${total_val:,.2f}")
    col2.metric("Total Gain/Loss", f"${total_pnl:,.2f}", delta=f"{(total_pnl/total_invested)*100:.1f}%")
    col3.metric("Active Positions", len(df))

    st.markdown("---")

    # --- THE "PUBLIC.COM" STYLE FEED ---
    # Split layout: Charts on left, Feed on right
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📈 Performance")
        # Visual: Bar chart of Gainers vs Losers
        fig = px.bar(
            enriched_df, 
            x="ticker", 
            y="unrealized_pnl", 
            color="unrealized_pnl",
            color_continuous_scale=["red", "green"],
            title="Unrealized P&L by Asset",
            hover_data=["quantity", "price", "current_price"]
        )
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("📢 Social Feed")
        # Create cards for each trade
        for index, row in enriched_df.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['user_name']}** {row['action']} **{row['quantity']} {row['ticker']}**")
                st.caption(f"Entry: ${row['price']} • Current: ${row['current_price']:.2f}")
                
                # Color code the return
                color = "green" if row['return_pct'] > 0 else "red"
                st.markdown(f"Return: :{color}[{row['return_pct']:.2f}%]")
                
                if row['reasoning']:
                    st.info(f"\"{row['reasoning']}\"")

else:
    st.info("No trades found. Use the sidebar to add your first position!")
