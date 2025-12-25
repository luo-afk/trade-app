import streamlit as st
import time
from utils.market import get_market_status

def render_top_bar():
    """Renders the Date, Market Status, and Search Bar"""
    
    # 1. Apply CSS
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # 2. Top Bar Layout
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # Market Status
        color, status, date_str = get_market_status()
        st.markdown(f"""
            <div style='margin-top: 5px;'>
                <span style='font-size: 14px; color: #888;'>{date_str}</span><br>
                <span style='color: {color}; font-weight: bold; font-size: 12px;'>● {status}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Stock Search
        search = st.text_input("Search", placeholder="Search stocks (e.g. AAPL)...", label_visibility="collapsed")
        
        if search:
            # Redirect logic: We save the ticker to session and reload to the Stock View
            st.session_state["selected_ticker"] = search.upper()
            st.switch_page("views/stock.py")
            
    st.divider()
