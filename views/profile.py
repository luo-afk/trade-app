import streamlit as st
import time
import base64
from utils.db import update_user_profile
from utils.ui_components import render_top_bar

st.session_state["current_page"] = "profile"
render_top_bar()

st.title("Settings")

current_user = st.session_state["user"]
current_avatar = current_user.get('avatar_url', 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y')

# Layout
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown(
        f"""
        <img src="{current_avatar}" style="border-radius: 50%; width: 120px; height: 120px; object-fit: cover; border: 2px solid #333;">
        """,
        unsafe_allow_html=True
    )

with col2:
    st.subheader(f"{current_user['full_name']}")
    st.caption(f"@{current_user['username']}")

st.divider()

# --- FORM ---
with st.form("profile_form"):
    st.markdown("### Profile Details")
    new_name = st.text_input("Display Name", value=current_user['full_name'])
    
    st.markdown("### Profile Picture")
    
    # 1. File Uploader
    uploaded_file = st.file_uploader("Upload new image", type=['png', 'jpg', 'jpeg'])
    
    # 2. Logic to convert file to Base64 string
    final_avatar_url = current_avatar
    if uploaded_file is not None:
        try:
            bytes_data = uploaded_file.getvalue()
            # Check size (limit to ~1MB to prevent DB bloat)
            if len(bytes_data) > 1_000_000:
                st.error("Image too large. Please use an image under 1MB.")
            else:
                b64 = base64.b64encode(bytes_data).decode()
                final_avatar_url = f"data:image/png;base64,{b64}"
                st.info("New image selected! Click 'Save Changes' to apply.")
        except:
            st.error("Error processing image.")

    st.markdown("### Security")
    new_password = st.text_input("New Password", type="password", value=current_user['password'])
    
    if st.form_submit_button("Save Changes", type="primary"):
        # Update DB
        update_user_profile(current_user['username'], new_name, new_password, final_avatar_url)
        
        # Update Session
        st.session_state["user"]["full_name"] = new_name
        st.session_state["user"]["password"] = new_password
        st.session_state["user"]["avatar_url"] = final_avatar_url
        
        st.success("Profile updated!")
        time.sleep(1)
        st.rerun()

st.divider()
if st.button("Log Out"):
    st.session_state["authenticated"] = False
    st.session_state["user"] = {}
    st.rerun()
