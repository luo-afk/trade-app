import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import time

# 1. Page Config
st.set_page_config(page_title="Family Alpha", page_icon="📈", layout="centered")

# 2. Connect to DB
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- NEW AUTHENTICATION LOGIC ---
def login_user(username, password):
    """Checks DB for username/password match"""
    try:
        # Query the users table
        response = supabase.table("users").select("*").eq("username", username).execute()
        # Check if user exists and password matches
        if len(response.data) > 0:
            user_data = response.data[0]
            if user_data['password'] == password:
                return user_data
    except Exception as e:
        st.error(f"Login Error: {e}")
    return None

def init_session():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["full_name"] = None

init_session()

# --- LOGIN SCREEN ---
if not st.session_state["authenticated"]:
    st.title("🔒 Family Trade Login")
    
    with st.form("login_form"):
        username = st.text_input("Username").lower().strip()
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log In")
        
        if submit:
            user = login_user(username, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["username"] = user['username']
                st.session_state["full_name"] = user['full_name']
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect username or password")
    
    st.stop()  # Stop here if not logged in

# --- MAIN APP (Only runs if logged in) ---

# Sidebar for Logout
with st.sidebar:
    st.write(f"Logged in as: **{st.session_state['full_name']}**")
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

st.title("📈 Family Trade Journal")
st.write(f"Welcome back, {st.session_state['full_name']}.")

# --- INPUT FORM (UPDATED) ---
# We removed the 'Who is trading?' selector because we know who it is now!
with st.expander("📝 Log a New Trade", expanded=False):
    with st.form("trade_form"):
        col1, col2 = st.columns(2)
        ticker = col1.text_input("Ticker (e.g. NVDA)").upper()
        action = col2.selectbox("Action", ["Buy", "Sell"])
        price = st.number_input("Price", min_value=0.01, step=0.01)
        reasoning = st.text_area("Why? (The Strategy)", placeholder="Earnings beat expectations...")
        
        submitted = st.form_submit_button("Log Trade")
        
        if submitted:
            data = {
                "user_name": st.session_state["username"],  # AUTOMATICALLY USE LOGGED IN USER
                "ticker": ticker,
                "action": action,
                "price": price,
                "reasoning": reasoning
            }
            supabase.table("trades").insert(data).execute()
            st.success(f"Logged {action} order for {ticker}!")
            time.sleep(1)
            st.rerun()

# --- DASHBOARD ---
st.divider()
st.subheader("📊 Active Portfolio")

# Fetch ALL trades (so they can see each other's trades)
# OR: Filter by .eq("user_name", st.session_state["username"]) if you want privacy
response = supabase.table("trades").select("*").order("created_at", desc=True).execute()
df = pd.DataFrame(response.data)

if not df.empty:
    st.metric("Total Trades Logged", len(df))
    
    # Show table
    st.dataframe(
        df[["created_at", "user_name", "ticker", "action", "price", "reasoning"]],
        hide_index=True,
        use_container_width=True
    )
    
    # Chart
    if 'user_name' in df.columns:
        trade_counts = df['user_name'].value_counts().reset_index()
        trade_counts.columns = ['User', 'Count']
        fig = px.bar(trade_counts, x='User', y='Count', title="Leaderboard", color="User")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No trades yet.")
