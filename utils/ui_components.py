import streamlit as st
import datetime
import pytz

def get_market_status():
    """Returns (Color, StatusText, DateString)"""
    tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(tz)
    is_weekday = now.weekday() < 5
    current_hour = now.hour + (now.minute / 60)
    is_open = is_weekday and (9.5 <= current_hour < 16.0)
    
    color = "#00FF00" if is_open else "#888888"
    status = "Market Open" if is_open else "Market Closed"
    return color, status, now.strftime("%B %d, %Y")

def render_top_bar():
    # Load CSS
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        color, status, date_str = get_market_status()
        st.markdown(f"""
            <div style='margin-top: 5px; font-family: sans-serif;'>
                <span style='font-size: 14px; color: #888;'>{date_str}</span><br>
                <span style='color: {color}; font-weight: bold; font-size: 12px; letter-spacing: 0.5px;'>● {status.upper()}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # SEARCH LOGIC FIX:
        def handle_search():
            # Only redirect if there is actual text
            if st.session_state["top_search"]:
                st.session_state["selected_ticker"] = st.session_state["top_search"].upper()
                st.session_state["top_search"] = "" # Clear box
                st.session_state["trigger_redirect"] = True # Set flag

        st.text_input(
            "Search", 
            key="top_search", 
            placeholder="Search assets...", 
            label_visibility="collapsed",
            on_change=handle_search
        )
        
        # Perform redirect only when flag is set
        if st.session_state.get("trigger_redirect"):
            st.session_state["trigger_redirect"] = False # Reset flag
            st.switch_page("views/stock.py")

    st.markdown("---")
