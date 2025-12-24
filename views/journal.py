import streamlit as st
import pandas as pd
from utils.db import get_trades, delete_trade

st.title("📖 Trade Journal")

col1, col2 = st.columns(2)
view_mode = col1.radio("View:", ["My Trades", "All Family Trades"], horizontal=True)

raw_data = get_trades()
df = pd.DataFrame(raw_data)

if not df.empty:
    if view_mode == "My Trades":
        df = df[df['user_name'] == st.session_state["user"]["username"]]

    for index, row in df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 1, 3, 0.5])
            
            color = "green" if row['action'] == "Buy" else "red"
            
            with c1:
                st.markdown(f"**{row['ticker']}**")
                st.caption(f"{row['created_at'][:10]}")
            with c2:
                st.markdown(f":{color}[{row['action']}] **{row['quantity']}** @ ${row['price']}")
            with c3:
                st.markdown(f"_{row['reasoning']}_")
                st.caption(f"Trader: {row['user_name']}")
            with c4:
                # Only allow deleting your own trades
                if row['user_name'] == st.session_state["user"]["username"]:
                    # Unique key is crucial here!
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        delete_trade(row['id'])
                        st.toast("Trade deleted!")
                        st.rerun()
else:
    st.info("No trades found.")
