import streamlit as st
import time
from utils.db import log_trade
from utils.market import get_current_price, get_common_tickers

st.title("➕ Log a New Trade")

# 1. Ticker Selection (Autocompletes from our list)
# We also allow them to type a custom one if it's not in the list.
common_tickers = get_common_tickers()

with st.container(border=True):
    st.subheader("1. Asset Details")
    
    # The 'index=None' makes it empty by default so they have to type/select
    ticker = st.selectbox(
        "Search Ticker (e.g. NVDA, VOO)", 
        options=common_tickers, 
        index=None,
        placeholder="Type to search..."
    )

    # Allow custom ticker if not in list
    if not ticker:
        manual_ticker = st.text_input("Or type a custom ticker manually:")
        if manual_ticker:
            ticker = manual_ticker.upper()

    # 2. Real-Time Price Check
    current_price = 0.0
    if ticker:
        with st.spinner(f"Fetching live price for {ticker}..."):
            current_price = get_current_price(ticker)
        
        if current_price:
            st.metric(label=f"Current Price of {ticker}", value=f"${current_price:,.2f}")
        else:
            st.error(f"Could not fetch price for {ticker}. Please enter manually below.")

    st.divider()

    # 3. Dynamic Entry (Shares vs. Dollars)
    st.subheader("2. Position Size")
    
    # Toggle Switch
    input_mode = st.radio("How do you want to enter this?", ["By Share Quantity", "By Total Amount ($)"], horizontal=True)

    col1, col2 = st.columns(2)
    
    final_qty = 0.0
    final_price = 0.0

    with col1:
        # Override price if they got a different fill
        entry_price = st.number_input("Fill Price", value=current_price, min_value=0.01, format="%.2f")

    with col2:
        if input_mode == "By Share Quantity":
            # Normal Mode: Enter Shares -> Calc Total
            qty_input = st.number_input("Number of Shares", min_value=0.01, step=1.0)
            if qty_input > 0:
                estimated_total = qty_input * entry_price
                st.info(f"Total Invested: **${estimated_total:,.2f}**")
                final_qty = qty_input
        else:
            # Smart Mode: Enter $$$ -> Calc Shares
            amount_input = st.number_input("Total Amount Spent ($)", min_value=1.0, step=10.0)
            if amount_input > 0 and entry_price > 0:
                calculated_shares = amount_input / entry_price
                st.info(f"This equals **{calculated_shares:.4f} shares**")
                final_qty = calculated_shares

    st.divider()

    # 4. Strategy & Submit
    st.subheader("3. Reasoning")
    action = st.selectbox("Action", ["Buy", "Sell"])
    reasoning = st.text_area("Thesis", placeholder="Why did you buy this? (Earnings, FOMO, Long-term hold...)")

    submit = st.button("Log Trade", type="primary", use_container_width=True)

    if submit:
        if ticker and final_qty > 0 and entry_price > 0:
            log_trade(
                st.session_state["user"]["username"], 
                ticker, 
                action, 
                entry_price, 
                final_qty, 
                reasoning
            )
            st.success(f"✅ Logged {action} {final_qty:.4f} shares of {ticker}!")
            time.sleep(2)
            st.switch_page("views/dashboard.py") # Auto redirect to dashboard
        else:
            st.error("Please ensure Ticker, Price, and Quantity are set.")

