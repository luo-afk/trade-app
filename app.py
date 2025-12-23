import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Makes it look like an app)
st.set_page_config(page_title="Family Alpha", page_icon="📈", layout="centered")

# 2. Connect to Database
# We will set these 'secrets' in the cloud dashboard later
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 3. The UI Styling
st.title("📈 Family Trade Journal")
st.write("Track your reasoning. Beat the market.")

# 4. Input Form
with st.expander("📝 Log a New Trade", expanded=False):
    with st.form("trade_form"):
        user = st.selectbox("Who is trading?", ["Mom", "Brother"])
        col1, col2 = st.columns(2)
        ticker = col1.text_input("Ticker (e.g. NVDA)").upper()
        action = col2.selectbox("Action", ["Buy", "Sell"])
        price = st.number_input("Price", min_value=0.01, step=0.01)
        reasoning = st.text_area("Why? (The Strategy)", placeholder="Earnings beat expectations, breaking out of 200 EMA...")
        
        submitted = st.form_submit_button("Log Trade")
        
        if submitted:
            data = {
                "user_name": user,
                "ticker": ticker,
                "action": action,
                "price": price,
                "reasoning": reasoning
            }
            supabase.table("trades").insert(data).execute()
            st.success(f"Logged {action} order for {ticker}!")
            st.rerun()

# 5. Dashboard (The "Nice Looking" Part)
st.divider()
st.subheader("📊 Active Portfolio")

# Fetch data from Supabase
response = supabase.table("trades").select("*").order("created_at", desc=True).execute()
df = pd.DataFrame(response.data)

if not df.empty:
    # Simple Metrics
    total_trades = len(df)
    st.metric("Total Trades Logged", total_trades)

    # Show the table but make it look clean
    st.dataframe(
        df[["created_at", "user_name", "ticker", "action", "price", "reasoning"]],
        hide_index=True,
        use_container_width=True
    )
    
    # Simple Chart: Who trades the most?
    trade_counts = df['user_name'].value_counts().reset_index()
    trade_counts.columns = ['User', 'Count']
    fig = px.bar(trade_counts, x='User', y='Count', title="Who is trading more?", color="User")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No trades logged yet. Be the first!")