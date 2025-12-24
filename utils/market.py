import streamlit as st
import yfinance as yf
import pandas as pd

@st.cache_data(ttl=300)  # Cache data for 5 minutes (prevents slow loading)
def get_current_price(ticker):
    try:
        data = yf.Ticker(ticker)
        # Fast fetch of just the latest price
        price = data.fast_info['last_price']
        return price
    except:
        return None

def calculate_portfolio_value(trades_df):
    """
    Takes the trades dataframe and adds 'Current Price' and 'PnL' columns.
    """
    if trades_df.empty:
        return 0, trades_df

    # Get unique tickers to fetch
    unique_tickers = trades_df['ticker'].unique()
    current_prices = {}
    
    # Fetch prices
    for t in unique_tickers:
        p = get_current_price(t)
        if p:
            current_prices[t] = p

    # Logic:
    # 1. Map current prices to the dataframe
    trades_df['current_price'] = trades_df['ticker'].map(current_prices)
    
    # 2. Calculate Market Value = Quantity * Current Price
    trades_df['market_value'] = trades_df['quantity'] * trades_df['current_price']
    
    # 3. Calculate Cost Basis = Quantity * Entry Price
    trades_df['cost_basis'] = trades_df['quantity'] * trades_df['price']
    
    # 4. Calculate PnL (Profit and Loss)
    # If it's a BUY: (Current - Entry) * Qty
    # If it's a SELL (Short): (Entry - Current) * Qty -- (Simplified for now assuming mostly Longs)
    trades_df['unrealized_pnl'] = trades_df['market_value'] - trades_df['cost_basis']
    trades_df['return_pct'] = (trades_df['unrealized_pnl'] / trades_df['cost_basis']) * 100
    
    total_value = trades_df['market_value'].sum()
    return total_value, trades_df

# utils/market.py (Add this to the bottom)

def get_common_tickers():
    """Returns a list of popular tickers for autocomplete"""
    # You can expand this list later!
    return [
        "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "NFLX", # Tech
        "SPY", "VOO", "VTI", "QQQ", "IWM", "DIA", "SCHD", "JEPI", # ETFs
        "JPM", "BAC", "WFC", "V", "MA", "AXP", # Finance
        "KO", "PEP", "MCD", "SBUX", "WMT", "TGT", # Consumer
        "DIS", "NKE", "HD", "LOW", "COST", # Retail
        "XOM", "CVX", "NEE", # Energy
        "JNJ", "PFE", "LLY", "UNH", # Healthcare
        "AMD", "INTC", "QCOM", "CRM", "ADBE" # Chips/Software
    ]
