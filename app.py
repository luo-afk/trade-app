import streamlit as st
from utils.auth import check_login

# 1. Config
st.set_page_config(
    page_title="WaddleWealth", 
    page_icon="https://img.icons8.com/color/96/duck.png", 
    layout="wide"
)

# 2. Sidebar Branding (The Top Slot)
# 'icon_image' is shown when collapsed, 'image' is shown when expanded.
# Since we don't have a wide image URL for text, we use the duck for both 
# and let the user know via the UI context or just keep it minimal.
st.logo(
    "https://img.icons8.com/color/96/duck.png", 
    link="https://google.com", 
    icon_image="https://img.icons8.com/color/96/duck.png"
)

# To add the text "WaddleWealth" next to it at the top, Streamlit requires
# a single image file containing both logo + text. 
# However, we can add a title right below the logo space if we want text separation.
# But st.logo is the only element that sits ABOVE navigation.

# 3. Auth
user = check_login()

# 4. Navigation
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
