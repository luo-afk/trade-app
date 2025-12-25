import streamlit as st
from utils.auth import check_login

# 1. Config
st.set_page_config(page_title="Family Alpha", page_icon="📈", layout="wide")

# 2. Auth
user = check_login()

# 3. Navigation with Professional Icons
if st.session_state["authenticated"]:
    
    pages = {
        "Main": [
            st.Page("views/dashboard.py", title="Portfolio", icon=":material/dashboard:", default=True),
            st.Page("views/leaderboard.py", title="Leaderboard", icon=":material/trophy:"),
        ],
        "Trading": [
            st.Page("views/entry.py", title="Trade", icon=":material/swap_horiz:"),
            st.Page("views/journal.py", title="History", icon=":material/history:"),
            st.Page("views/stock.py", title="Research", icon=":material/search:"), # New Page
        ],
        "Account": [
            st.Page("views/profile.py", title="Settings", icon=":material/settings:"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()
