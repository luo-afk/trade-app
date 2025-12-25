import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300) # Cache 5 mins for live-ish data
def get_portfolio_history(trades_df, period="1d", interval="5m"):
    """
    Reconstructs the portfolio value over time.
    Supports intraday intervals (5m, 15m) for the 'Live' feel.
    """
    if trades_df.empty:
        return pd.DataFrame()

    tickers = trades_df['ticker'].unique().tolist()
    
    # 1. Download Data with specific interval
    try:
        data = yf.download(tickers, period=period, interval=interval, progress=False, group_by='ticker')
    except:
        return pd.DataFrame()

    # 2. Extract Close Prices
    history = pd.DataFrame()
    if len(tickers) == 1:
        t = tickers[0]
        if 'Close' in data.columns:
            history[t] = data['Close']
        else:
            try:
                history[t] = data.iloc[:, 3] 
            except:
                pass
    else:
        for t in tickers:
            try:
                if (t, 'Close') in data.columns:
                    history[t] = data[(t, 'Close')]
                elif t in data.columns and 'Close' in data[t].columns:
                     history[t] = data[t]['Close']
            except:
                pass

    # Forward fill to handle gaps in intraday data
    history = history.ffill()
    
    # If history is empty (e.g. market just opened or bad query), return empty
    if history.empty:
        return pd.DataFrame()

    # 3. Reconstruct Portfolio
    portfolio_history = []
    
    # Pre-process trades: Ensure timestamps are timezone-aware if history is
    trades_df['created_at'] = pd.to_datetime(trades_df['created_at'])
    
    # Check if history index is timezone aware
    is_tz_aware = history.index.tz is not None
    
    for date in history.index:
        # Align Timezones
        current_ts = date
        if is_tz_aware and trades_df['created_at'].dt.tz is None:
             # Localize trades if they aren't but history is
             trade_dates = trades_df['created_at'].dt.tz_localize(date.tz)
        elif not is_tz_aware and trades_df['created_at'].dt.tz is not None:
             # Naive history, strip trade tz
             trade_dates = trades_df['created_at'].dt.tz_localize(None)
        else:
             trade_dates = trades_df['created_at']

        # Filter trades that happened BEFORE this timestamp
        mask = trade_dates <= current_ts
        relevant_trades = trades_df[mask]
        
        if relevant_trades.empty:
            continue

        holdings = {}
        cost_basis = 0.0
        
        for _, trade in relevant_trades.iterrows():
            qty = float(trade['quantity'])
            price = float(trade['price'])
            sym = trade['ticker']
            
            if sym not in holdings: holdings[sym] = 0.0
            
            if trade['action'] == "Buy":
                holdings[sym] += qty
                cost_basis += (qty * price)
            elif trade['action'] == "Sell":
                holdings[sym] -= qty
                cost_basis -= (qty * price)

        # Calculate Value
        daily_val = 0.0
        for sym, shares in holdings.items():
            if shares > 0:
                price_now = 0
                # Try to get price at this specific minute
                if sym in history.columns:
                    val = history.loc[date, sym]
                    if pd.notna(val):
                        price_now = val
                
                daily_val += shares * price_now
        
        # Avoid division by zero
        if cost_basis == 0:
            pct = 0.0
        else:
            pct = ((daily_val - cost_basis) / cost_basis) * 100

        portfolio_history.append({
            "Date": date,
            "Portfolio Value": daily_val,
            "Cost Basis": cost_basis,
            "Return %": pct
        })

    return pd.DataFrame(portfolio_history)

@st.cache_data(ttl=300)
def get_benchmark_history(ticker, period="1d", interval="5m"):
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)['Close']
        if data.empty: return pd.DataFrame()
        
        start = data.iloc[0]
        normalized = ((data - start) / start) * 100
        df = normalized.reset_index()
        df.columns = ["Date", "Return %"]
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
