import os
import requests
from typing import Optional, Literal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

####################################
# API Configuration
####################################

# Check which provider to use (defaults to yfinance for free tier)
USE_FINANCIAL_DATASETS = os.getenv("FINANCIAL_DATASETS_API_KEY") is not None and os.getenv("USE_FINANCIAL_DATASETS", "false").lower() == "true"
financial_datasets_api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")

# Import yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    logger.info("yfinance library loaded successfully")
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance not available - install with: pip install yfinance")

####################################
# Financial Datasets API Functions
####################################

def call_api(endpoint: str, params: dict) -> dict:
    """Helper function to call the Financial Datasets API."""
    if not USE_FINANCIAL_DATASETS:
        raise ValueError("Financial Datasets API key not configured or USE_FINANCIAL_DATASETS not set to true")

    base_url = "https://api.financialdatasets.ai"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": financial_datasets_api_key}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

####################################
# yfinance Provider Functions
####################################

def get_yf_income_statement(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10
) -> list:
    """Fetch income statement from yfinance."""
    if not YFINANCE_AVAILABLE:
        raise ValueError("yfinance not available - install with: pip install yfinance")

    stock = yf.Ticker(ticker)

    if period == "annual":
        df = stock.income_stmt
    elif period == "quarterly":
        df = stock.quarterly_income_stmt
    else:  # ttm
        df = stock.income_stmt  # Use annual as approximation

    if df is None or df.empty:
        return []

    # Convert to list of dicts (limited to requested number)
    results = []
    for col in df.columns[:limit]:
        stmt = {"report_period": col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col)}
        for idx in df.index:
            # Clean up the field name
            field_name = str(idx).replace(" ", "_").lower()
            stmt[field_name] = float(df.loc[idx, col]) if not pd.isna(df.loc[idx, col]) else None
        results.append(stmt)

    return results

def get_yf_balance_sheet(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10
) -> list:
    """Fetch balance sheet from yfinance."""
    if not YFINANCE_AVAILABLE:
        raise ValueError("yfinance not available - install with: pip install yfinance")

    stock = yf.Ticker(ticker)

    if period == "annual":
        df = stock.balance_sheet
    elif period == "quarterly":
        df = stock.quarterly_balance_sheet
    else:  # ttm
        df = stock.balance_sheet

    if df is None or df.empty:
        return []

    results = []
    for col in df.columns[:limit]:
        stmt = {"report_period": col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col)}
        for idx in df.index:
            field_name = str(idx).replace(" ", "_").lower()
            stmt[field_name] = float(df.loc[idx, col]) if not pd.isna(df.loc[idx, col]) else None
        results.append(stmt)

    return results

def get_yf_cash_flow(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10
) -> list:
    """Fetch cash flow statement from yfinance."""
    if not YFINANCE_AVAILABLE:
        raise ValueError("yfinance not available - install with: pip install yfinance")

    stock = yf.Ticker(ticker)

    if period == "annual":
        df = stock.cashflow
    elif period == "quarterly":
        df = stock.quarterly_cashflow
    else:  # ttm
        df = stock.cashflow

    if df is None or df.empty:
        return []

    results = []
    for col in df.columns[:limit]:
        stmt = {"report_period": col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col)}
        for idx in df.index:
            field_name = str(idx).replace(" ", "_").lower()
            stmt[field_name] = float(df.loc[idx, col]) if not pd.isna(df.loc[idx, col]) else None
        results.append(stmt)

    return results

def get_yf_price_snapshot(ticker: str) -> dict:
    """Fetch current price snapshot from yfinance."""
    if not YFINANCE_AVAILABLE:
        raise ValueError("yfinance not available - install with: pip install yfinance")

    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "ticker": ticker,
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "open": info.get("regularMarketOpen"),
        "high": info.get("regularMarketDayHigh"),
        "low": info.get("regularMarketDayLow"),
        "close": info.get("regularMarketPreviousClose"),
        "volume": info.get("regularMarketVolume"),
        "market_cap": info.get("marketCap"),
        "timestamp": datetime.now().isoformat()
    }

def get_yf_prices(
    ticker: str,
    interval: Literal["minute", "day", "week", "month", "year"],
    interval_multiplier: int,
    start_date: str,
    end_date: str
) -> list:
    """Fetch historical prices from yfinance."""
    if not YFINANCE_AVAILABLE:
        raise ValueError("yfinance not available - install with: pip install yfinance")

    # Map interval to yfinance format
    interval_map = {
        "minute": f"{interval_multiplier}m",
        "day": f"{interval_multiplier}d",
        "week": "1wk",
        "month": "1mo",
        "year": "1y"
    }

    yf_interval = interval_map.get(interval, "1d")

    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date, interval=yf_interval)

    if df is None or df.empty:
        return []

    results = []
    for idx, row in df.iterrows():
        results.append({
            "date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx),
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close']),
            "volume": int(row['Volume'])
        })

    return results

def get_yf_financial_metrics(ticker: str, period: Literal["annual", "quarterly", "ttm"] = "ttm") -> dict:
    """Fetch financial metrics snapshot from yfinance."""
    if not YFINANCE_AVAILABLE:
        raise ValueError("yfinance not available - install with: pip install yfinance")

    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "ticker": ticker,
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "price_to_book": info.get("priceToBook"),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        "enterprise_value": info.get("enterpriseValue"),
        "ev_to_revenue": info.get("enterpriseToRevenue"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "profit_margin": info.get("profitMargins"),
        "operating_margin": info.get("operatingMargins"),
        "return_on_assets": info.get("returnOnAssets"),
        "return_on_equity": info.get("returnOnEquity"),
        "revenue": info.get("totalRevenue"),
        "revenue_per_share": info.get("revenuePerShare"),
        "earnings_per_share": info.get("trailingEps"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "52_week_high": info.get("fiftyTwoWeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow")
    }

# Add pandas import for dataframe handling
try:
    import pandas as pd
except ImportError:
    logger.warning("pandas not available - some yfinance features may not work")

####################################
# Provider Selection
####################################

def get_provider_status() -> dict:
    """Get the current provider configuration."""
    return {
        "provider": "financial_datasets" if USE_FINANCIAL_DATASETS else "yfinance",
        "financial_datasets_available": financial_datasets_api_key is not None,
        "yfinance_available": YFINANCE_AVAILABLE
    }
