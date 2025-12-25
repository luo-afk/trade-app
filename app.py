import streamlit as st
from utils.auth import check_login

# 1. Config - WaddleWealth Branding
st.set_page_config(
    page_title="WaddleWealth", 
    page_icon="https://img.icons8.com/color/96/duck.png", 
    layout="wide"
)

# 2. Auth
user = check_login()

# 3. Navigation
if st.session_state["authenticated"]:
    
    pages = {
        "Portfolio": [
            st.Page("views/dashboard.py", title="Home", icon=":material/home:", default=True),
            st.Page("views/compare.py", title="Compare", icon=":material/compare_arrows:"),
            st.Page("views/leaderboard.py", title="Leaderboard", icon=":material/trophy:"),
        ],
        "Discover": [
            st.Page("views/stock.py", title="Research", icon=":material/search:"),
            st.Page("views/journal.py", title="History", icon=":material/history:"),
        ],
        "Actions": [
            st.Page("views/entry.py", title="Trade", icon=":material/swap_horiz:"),
            st.Page("views/profile.py", title="Settings", icon=":material/settings:"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()
