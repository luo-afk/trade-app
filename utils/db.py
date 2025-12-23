import streamlit as st
from supabase import create_client, Client

# Initialize connection once and cache it
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def log_trade(user, ticker, action, price, quantity, reasoning):
    data = {
        "user_name": user,
        "ticker": ticker,
        "action": action,
        "price": price,
        "quantity": quantity,
        "reasoning": reasoning
    }
    supabase.table("trades").insert(data).execute()

def get_trades():
    response = supabase.table("trades").select("*").order("created_at", desc=True).execute()
    return response.data

def get_users():
    return supabase.table("users").select("*").execute().data
