import streamlit as st
from utils.db import get_users

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = {}

    if not st.session_state["authenticated"]:
        st.title("🔒 Family Trade Login")
        with st.form("login"):
            username = st.text_input("Username").lower().strip()
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Log In"):
                users = get_users()
                # Find user
                valid_user = next((u for u in users if u['username'] == username and u['password'] == password), None)
                if valid_user:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = valid_user
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        st.stop()
    
    return st.session_state["user"]
