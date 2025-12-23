import streamlit as st
from utils.auth import check_login

# 1. Page Config (Global)
st.set_page_config(page_title="Family Alpha", page_icon="📈", layout="wide")

# 2. Authentication Check
# This runs before anything else. If not logged in, it stops here.
user = check_login()

# 3. Navigation Setup (Only happens if logged in)
if st.session_state["authenticated"]:
    
    # Define the pages
    pages = {
        "Portfolio": [
            st.Page("views/dashboard.py", title="Overview & Compare", icon="📊", default=True),
            st.Page("views/entry.py", title="Log a Trade", icon="➕"),
            st.Page("views/journal.py", title="Trade Journal", icon="📖"),
        ],
        "Intelligence": [
            st.Page("views/analysis.py", title="AI Analysis", icon="🧠"),
        ]
    }

    # Run the navigation
    pg = st.navigation(pages)
    
    # Optional: Add a logo to the sidebar
    st.logo("https://img.icons8.com/ios-filled/50/FFFFFF/bullish.png", icon_image="https://img.icons8.com/ios-filled/50/FFFFFF/bullish.png")
    
    st.sidebar.text(f"👤 {user['full_name']}")
    
    pg.run()
