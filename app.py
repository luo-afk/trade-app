import streamlit as st
from utils.auth import check_login

# 1. Page Config (Global)
st.set_page_config(page_title="Family Alpha", page_icon="📈", layout="wide")

# 2. Authentication Check
# This runs before anything else. If not logged in, it stops here.
user = check_login()

# 3. Navigation Setup (Only happens if logged in)
# ... (Previous imports and auth check) ...

if st.session_state["authenticated"]:

    # 1. Define the pages (Added 'Settings' category)
    pages = {
        "Portfolio": [
            st.Page("views/dashboard.py", title="Overview", icon="📊", default=True),
            st.Page("views/entry.py", title="Log a Trade", icon="➕"),
            st.Page("views/journal.py", title="Trade Journal", icon="📖"),
        ],
        "Intelligence": [
            st.Page("views/analysis.py", title="AI Analysis", icon="🧠"),
        ],
        "Settings": [
            st.Page("views/profile.py", title="My Profile", icon="👤"),
        ]
    }

    pg = st.navigation(pages)

    # 2. Sidebar Customization
    st.sidebar.markdown("---")

    # This creates the "Clickable" User Profile
    # It links directly to the views/profile.py page
    # st.sidebar.page_link("views/profile.py", label=st.session_state["user"]["full_name"], icon="👤")

    # Optional: Keep the logout button in sidebar as a backup,
    # but we also have it on the profile page now.

    pg.run()
