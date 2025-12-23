import streamlit as st
from utils.db import log_trade

st.title("➕ Log a New Trade")

with st.container(border=True):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("💡 **Tip:** Be honest with your reasoning. That is how the AI helps you.")
    
    with col2:
        with st.form("trade_form", clear_on_submit=True):
            row1_1, row1_2 = st.columns(2)
            ticker = row1_1.text_input("Ticker Symbol").upper()
            action = row1_2.selectbox("Action", ["Buy", "Sell"])
            
            row2_1, row2_2 = st.columns(2)
            qty = row2_1.number_input("Shares", min_value=0.01, step=1.0)
            price = row2_2.number_input("Price per Share", min_value=0.01, step=0.01)
            
            reasoning = st.text_area("Why are you taking this trade?", placeholder="e.g. Breaking out of 200 EMA, Earnings beat...")
            
            if st.form_submit_button("Submit Trade", type="primary"):
                if ticker and price > 0:
                    log_trade(st.session_state["user"]["username"], ticker, action, price, qty, reasoning)
                    st.success(f"Successfully logged {action} for {ticker}")
                else:
                    st.error("Please fill in valid details.")
