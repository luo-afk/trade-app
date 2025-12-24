import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600) # Cache for 1 hour so we don't spam Yahoo
def get_portfolio_history(trades_df, period="1mo"):
    """
    Reconstructs the daily portfolio value based on trade history.
    Returns a DataFrame with Date, TotalValue, and InvestedAmount.
    """
    if trades_df.empty:
        return pd.DataFrame()

    # 1. Get list of all tickers ever traded
    tickers = trades_df['ticker'].unique().tolist()
    
    # 2. Download historical data for all tickers at once
    # We add a buffer to the period to ensure we have data for the start calculation
    history = yf.download(tickers, period=period, progress=False)['Close']
    
    # Handle single ticker case (yfinance formatting weirdness)
    if len(tickers) == 1:
        history = history.to_frame(name=tickers[0])
    
    # Fill missing weekends/holidays with the previous Friday's price
    history = history.ffill()

    # 3. Create a timeline of daily values
    portfolio_history = []

    # Iterate through every day in the downloaded history
    for date in history.index:
        # Find trades that happened ON or BEFORE this specific date
        # We assume trade entry_date is timezone-naive or we strip tz for comparison
        date_tz_naive = date.tz_localize(None)
        
        relevant_trades = trades_df[pd.to_datetime(trades_df['created_at']).dt.tz_localize(None) <= date_tz_naive]
        
        if relevant_trades.empty:
            continue
            
        # Calculate holdings for this specific day
        # (Group by ticker and sum the Buy/Sell quantities)
        holdings = {}
        cost_basis = 0.0
        
        for _, trade in relevant_trades.iterrows():
            qty = float(trade['quantity'])
            price = float(trade['price'])
            
            if trade['ticker'] not in holdings:
                holdings[trade['ticker']] = 0.0
            
            if trade['action'] == "Buy":
                holdings[trade['ticker']] += qty
                cost_basis += (qty * price)
            elif trade['action'] == "Sell":
                holdings[trade['ticker']] -= qty
                # Simplified cost basis reduction for selling
                cost_basis -= (qty * price) 

        # Calculate Total Market Value for this day
        daily_value = 0.0
        for ticker, shares in holdings.items():
            if shares > 0:
                # Get the price of that ticker on that specific day
                if ticker in history.columns:
                    # Use .loc with nearest valid index if exact match fails
                    try:
                        daily_price = history.loc[date, ticker]
                        daily_value += shares * daily_price
                    except:
                        pass # Price missing for this day
        
        # Calculate Return %
        pct_return = ((daily_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0

        portfolio_history.append({
            "Date": date,
            "Portfolio Value": daily_value,
            "Cost Basis": cost_basis,
            "Return %": pct_return
        })

    return pd.DataFrame(portfolio_history)

@st.cache_data(ttl=3600)
def get_benchmark_history(ticker, period="1mo"):
    """Fetches a benchmark (like SPY) and normalizes it to % return"""
    data = yf.Ticker(ticker).history(period=period)['Close']
    if data.empty:
        return pd.DataFrame()
    
    # Normalize: (Price - StartPrice) / StartPrice * 100
    start_price = data.iloc[0]
    normalized = ((data - start_price) / start_price) * 100
    
    df = normalized.reset_index()
    df.columns = ["Date", "Return %"]
    df['Type'] = ticker # Label for the chart
    return df
