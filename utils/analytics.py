import pandas as pd
import yfinance as yf
import streamlit as st

# ... (Keep your existing get_benchmark_history function) ...

@st.cache_data(ttl=3600)
def get_portfolio_history(trades_df, period="1mo"):
    # ... (Keep existing logic up until the return statement) ...
    # [PASTE YOUR EXISTING FUNCTION HERE, BUT REPLACE THE RETURN STATEMENT WITH THIS:]
    
    # ... previous code ...
    
    result_df = pd.DataFrame(portfolio_history)
    
    # --- FIX FOR FLAT LINE / 1D DATA ---
    if result_df.empty and not trades_df.empty:
        # If we have trades but yfinance returned nothing (e.g. market just opened),
        # Create a synthetic flat line for "Today"
        now = pd.Timestamp.now()
        start = now - pd.Timedelta(hours=24)
        
        # Calculate rough current value
        # (Simplified: just sum cost basis)
        est_val = (trades_df['quantity'] * trades_df['price']).sum()
        
        result_df = pd.DataFrame([
            {"Date": start, "Return %": 0.0, "Portfolio Value": est_val},
            {"Date": now, "Return %": 0.0, "Portfolio Value": est_val}
        ])
    
    elif len(result_df) == 1:
        # If we only have 1 data point, duplicate it so the line chart draws a flat line
        # instead of a single invisible dot.
        row = result_df.iloc[0].to_dict()
        row['Date'] = row['Date'] + pd.Timedelta(minutes=1) # Add 1 minute
        result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)

    return result_df

# --- NEW HELPER FOR LEADERBOARD ---
@st.cache_data(ttl=3600)
def get_bulk_history(tickers, period="1mo"):
    """Fetches simple % return history for a list of tickers (Users or ETFs)"""
    if not tickers:
        return pd.DataFrame()
    
    try:
        # Fetch all at once
        data = yf.download(tickers, period=period, progress=False)['Close']
        
        # Clean up if single ticker
        if len(tickers) == 1:
            data = data.to_frame(name=tickers[0])
            
        # Calculate % Return ((Current - Start) / Start)
        # We only need the final number for the leaderboard ranking
        results = []
        for t in tickers:
            if t in data.columns:
                series = data[t].dropna()
                if not series.empty:
                    start = series.iloc[0]
                    end = series.iloc[-1]
                    pct = ((end - start) / start) * 100
                    results.append({"Name": t, "Return %": pct})
        
        return pd.DataFrame(results)
    except Exception as e:
        return pd.DataFrame()
