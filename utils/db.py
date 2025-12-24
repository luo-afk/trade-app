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

def update_user_profile(username, new_full_name, new_password, new_avatar_url):
    """Updates the user's password, display name, and avatar"""
    data = {
        "full_name": new_full_name,
        "password": new_password,
        "avatar_url": new_avatar_url
    }
    supabase.table("users").update(data).eq("username", username).execute()

def delete_trade(trade_id):
    """Deletes a specific trade by ID"""
    supabase.table("trades").delete().eq("id", trade_id).execute()
