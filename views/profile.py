import streamlit as st
import time
from utils.db import update_user_profile

st.title("👤 User Profile")

# Get current user details
current_user = st.session_state["user"]

col1, col2 = st.columns([1, 2])

with col1:
    # Display a big avatar icon
    st.image("https://img.icons8.com/bubbles/200/user.png", width=150)

with col2:
    st.subheader(f"{current_user['full_name']}")
    st.caption(f"Username: @{current_user['username']}")

st.divider()

# --- EDIT PROFILE FORM ---
st.subheader("⚙️ Account Settings")

with st.form("profile_form"):
    new_name = st.text_input("Display Name", value=current_user['full_name'])
    new_password = st.text_input("New Password", type="password", value=current_user['password'])
    
    confirm_password = st.text_input("Confirm New Password", type="password", value=current_user['password'])
    
    if st.form_submit_button("Save Changes", type="primary"):
        if new_password != confirm_password:
            st.error("Passwords do not match!")
        else:
            # 1. Update Database
            update_user_profile(current_user['username'], new_name, new_password)
            
            # 2. Update Local Session
            st.session_state["user"]["full_name"] = new_name
            st.session_state["user"]["password"] = new_password
            
            st.success("Profile updated successfully!")
            time.sleep(1)
            st.rerun()

st.divider()

# --- LOGOUT BUTTON ---
if st.button("🚪 Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user"] = {}
    st.rerun()
