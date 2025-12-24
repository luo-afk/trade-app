import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600) 
def get_portfolio_history(trades_df, period="1mo"):
    """
    Reconstructs the daily portfolio value based on trade history.
    Returns a DataFrame with Date, TotalValue, and InvestedAmount.
    """
    if trades_df.empty:
        return pd.DataFrame()

    # 1. Get list of all tickers ever traded
    tickers = trades_df['ticker'].unique().tolist()
    
    # 2. Download historical data
    try:
        data = yf.download(tickers, period=period, progress=False, group_by='ticker')
    except:
        return pd.DataFrame()

    # 3. Extract "Close" prices safely
    history = pd.DataFrame()
    
    if len(tickers) == 1:
        # Single ticker case
        ticker = tickers[0]
        if 'Close' in data.columns:
            history[ticker] = data['Close']
        else:
            try:
                history[ticker] = data.iloc[:, 3] # Fallback
            except:
                pass
    else:
        # Multiple tickers
        for t in tickers:
            try:
                if (t, 'Close') in data.columns:
                    history[t] = data[(t, 'Close')]
                elif t in data.columns and 'Close' in data[t].columns:
                     history[t] = data[t]['Close']
            except:
                pass

    # Fill missing weekends/holidays
    history = history.ffill()

    # 4. Create a timeline of daily values
    portfolio_history = []

    # Iterate through every day in the downloaded history
    for date in history.index:
        # Ensure date comparison is timezone-naive
        date_naive = date.tz_localize(None) if date.tzinfo else date
        
        # Find trades that happened ON or BEFORE this specific date
        trades_df['created_at'] = pd.to_datetime(trades_df['created_at'])
        mask = trades_df['created_at'].apply(lambda x: x.tz_localize(None) if x.tzinfo else x) <= date_naive
        relevant_trades = trades_df[mask]
        
        if relevant_trades.empty:
            continue
            
        # Calculate holdings for this specific day
        holdings = {}
        cost_basis = 0.0
        
        for _, trade in relevant_trades.iterrows():
            qty = float(trade['quantity'])
            price = float(trade['price'])
            t_symbol = trade['ticker']
            
            if t_symbol not in holdings:
                holdings[t_symbol] = 0.0
            
            if trade['action'] == "Buy":
                holdings[t_symbol] += qty
                cost_basis += (qty * price)
            elif trade['action'] == "Sell":
                holdings[t_symbol] -= qty
                cost_basis -= (qty * price) 

        # Calculate Total Market Value for this day
        daily_value = 0.0
        for ticker, shares in holdings.items():
            if shares > 0:
                if ticker in history.columns:
                    try:
                        daily_price = history.loc[date, ticker]
                        if pd.notna(daily_price):
                            daily_value += shares * daily_price
                    except:
                        pass
        
        # Calculate Return %
        pct_return = ((daily_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0

        portfolio_history.append({
            "Date": date,
            "Portfolio Value": daily_value,
            "Cost Basis": cost_basis,
            "Return %": pct_return
        })

    result_df = pd.DataFrame(portfolio_history)

    # --- FIX FOR FLAT LINE / 1D DATA ---
    if result_df.empty and not trades_df.empty:
        # If we have trades but yfinance returned nothing (e.g. market just opened or 1d view),
        # Create a synthetic flat line
        now = pd.Timestamp.now()
        start = now - pd.Timedelta(hours=24)
        
        # Calculate rough current value
        est_val = (trades_df['quantity'] * trades_df['price']).sum()
        
        result_df = pd.DataFrame([
            {"Date": start, "Return %": 0.0, "Portfolio Value": est_val},
            {"Date": now, "Return %": 0.0, "Portfolio Value": est_val}
        ])
    
    elif len(result_df) == 1:
        # Duplicate single point to make a line
        row = result_df.iloc[0].to_dict()
        row['Date'] = row['Date'] + pd.Timedelta(minutes=1)
        result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)

    return result_df

@st.cache_data(ttl=3600)
def get_benchmark_history(ticker, period="1mo"):
    """Fetches a benchmark (like SPY) and normalizes it to % return"""
    try:
        data = yf.Ticker(ticker).history(period=period)['Close']
        if data.empty:
            return pd.DataFrame()
        
        # Normalize
        start_price = data.iloc[0]
        normalized = ((data - start_price) / start_price) * 100
        
        df = normalized.reset_index()
        df.columns = ["Date", "Return %"]
        
        # Handle timezone
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        
        return df
    except:
        return pd.DataFrame()

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
