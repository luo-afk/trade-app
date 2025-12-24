import streamlit as st
import time
from utils.db import update_user_profile

st.title("👤 User Profile")

# Get current user details from session
current_user = st.session_state["user"]

# Default to the gray image if they have None in DB
current_avatar = current_user.get('avatar_url', 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y')

col1, col2 = st.columns([1, 3])

with col1:
    # Display the Circular Image
    st.markdown(
        f"""
        <style>
            .profile-pic {{
                border-radius: 50%;
                width: 150px;
                height: 150px;
                object-fit: cover;
                border: 3px solid #00FF7F;
            }}
        </style>
        <img src="{current_avatar}" class="profile-pic">
        """,
        unsafe_allow_html=True
    )

with col2:
    st.header(f"{current_user['full_name']}")
    st.caption(f"Username: @{current_user['username']}")

st.divider()

# --- EDIT PROFILE FORM ---
st.subheader("⚙️ Account Settings")

with st.form("profile_form"):
    new_name = st.text_input("Display Name", value=current_user['full_name'])
    
    # --- Avatar Selection Section ---
    st.markdown("### 🖼️ Change Profile Picture")
    
    # Custom URL Input
    new_avatar = st.text_input("Image URL", value=current_avatar)
    
    # "Quick Select" Presets (For ease of use)
    st.caption("Or copy one of these presets:")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.code("https://img.icons8.com/color/480/bear.png", language=None)
    with c2: st.code("https://img.icons8.com/color/480/cat.png", language=None)
    with c3: st.code("https://img.icons8.com/color/480/bull.png", language=None) 
    with c4: st.code("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", language=None) # Reset to default

    st.divider()
    
    # Password Section
    st.markdown("### 🔒 Security")
    new_password = st.text_input("New Password", type="password", value=current_user['password'])
    confirm_password = st.text_input("Confirm New Password", type="password", value=current_user['password'])
    
    if st.form_submit_button("Save Changes", type="primary"):
        if new_password != confirm_password:
            st.error("Passwords do not match!")
        else:
            # 1. Update Database
            update_user_profile(
                current_user['username'], 
                new_name, 
                new_password,
                new_avatar
            )
            
            # 2. Update Local Session immediately so they see changes
            st.session_state["user"]["full_name"] = new_name
            st.session_state["user"]["password"] = new_password
            st.session_state["user"]["avatar_url"] = new_avatar
            
            st.success("Profile updated successfully!")
            time.sleep(1)
            st.rerun()

st.divider()

if st.button("🚪 Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user"] = {}
    st.rerun()
