import streamlit as st
import pandas as pd
from utils.db import get_trades

st.title("📖 Trade Journal")

# Filter controls
col1, col2 = st.columns(2)
view_mode = col1.radio("View:", ["My Trades", "All Family Trades"], horizontal=True)

# Fetch Data
raw_data = get_trades()
df = pd.DataFrame(raw_data)

if not df.empty:
    # Filter if "My Trades" is selected
    if view_mode == "My Trades":
        df = df[df['user_name'] == st.session_state["user"]["username"]]

    # Display loop (Cards view)
    for index, row in df.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1, 3])
            
            # Badge color
            color = "green" if row['action'] == "Buy" else "red"
            
            with c1:
                st.markdown(f"**{row['ticker']}**")
                st.caption(f"{row['created_at'][:10]}")
            with c2:
                st.markdown(f":{color}[{row['action']}] **{row['quantity']}** @ ${row['price']}")
            with c3:
                st.markdown(f"_{row['reasoning']}_")
                st.caption(f"Trader: {row['user_name']}")
else:
    st.info("No trades found.")
