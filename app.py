import streamlit as st
from utils.auth import check_login

# 1. Config - Professional Icon
st.set_page_config(page_title="Family Alpha", page_icon="🏛️", layout="wide")

# 2. Auth
user = check_login()

# 3. Navigation - Professional Material Icons
if st.session_state["authenticated"]:
    
    pages = {
        "Overview": [
            st.Page("views/dashboard.py", title="Portfolio", icon=":material/account_balance_wallet:", default=True),
            st.Page("views/compare.py", title="Compare", icon=":material/compare_arrows:"),
            st.Page("views/leaderboard.py", title="Leaderboard", icon=":material/leaderboard:"),
        ],
        "Market": [
            st.Page("views/stock.py", title="Research", icon=":material/search:"),
            st.Page("views/entry.py", title="Trade", icon=":material/trending_up:"),
            st.Page("views/journal.py", title="History", icon=":material/receipt_long:"),
        ],
        "Account": [
            st.Page("views/profile.py", title="Settings", icon=":material/person:"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()
