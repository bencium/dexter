from langchain.tools import tool
from typing import Literal, Optional
from pydantic import BaseModel, Field
from dexter.tools.api import call_api, USE_FINANCIAL_DATASETS, get_yf_income_statement, get_yf_balance_sheet, get_yf_cash_flow

####################################
# Tools
####################################

class FinancialStatementsInput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol to fetch financial statements for. For example, 'AAPL' for Apple.")
    period: Literal["annual", "quarterly", "ttm"] = Field(description="The reporting period for the financial statements. 'annual' for yearly, 'quarterly' for quarterly, and 'ttm' for trailing twelve months.")
    limit: int = Field(default=10, description="The number of past financial statements to retrieve.")
    report_period_gt: Optional[str] = Field(default=None, description="Filter for financial statements with report periods after this date (YYYY-MM-DD).")
    report_period_gte: Optional[str] = Field(default=None, description="Filter for financial statements with report periods on or after this date (YYYY-MM-DD).")
    report_period_lt: Optional[str] = Field(default=None, description="Filter for financial statements with report periods before this date (YYYY-MM-DD).")
    report_period_lte: Optional[str] = Field(default=None, description="Filter for financial statements with report periods on or before this date (YYYY-MM-DD).")


def _create_params(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int,
    report_period_gt: Optional[str],
    report_period_gte: Optional[str],
    report_period_lt: Optional[str],
    report_period_lte: Optional[str]
) -> dict:
    """Helper function to create params dict for API calls."""
    params = {"ticker": ticker, "period": period, "limit": limit}
    if report_period_gt is not None:
        params["report_period_gt"] = report_period_gt
    if report_period_gte is not None:
        params["report_period_gte"] = report_period_gte
    if report_period_lt is not None:
        params["report_period_lt"] = report_period_lt
    if report_period_lte is not None:
        params["report_period_lte"] = report_period_lte
    return params

@tool(args_schema=FinancialStatementsInput)
def get_income_statements(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None
) -> dict:
    """
    Fetches a company's income statements,
    detailing its revenues, expenses, net income, etc. over a reporting period.
    Useful for evaluating a company's profitability and operational efficiency.
    """
    if USE_FINANCIAL_DATASETS:
        params = _create_params(ticker, period, limit, report_period_gt, report_period_gte, report_period_lt, report_period_lte)
        data = call_api("/financials/income-statements/", params)
        return data.get("income_statements", {})
    else:
        # Use yfinance
        return get_yf_income_statement(ticker, period, limit)

@tool(args_schema=FinancialStatementsInput)
def get_balance_sheets(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None
) -> dict:
    """
    Retrieves a company's balance sheets, providing a snapshot of
    its assets, liabilities, shareholders' equity, etc. at a specific point in time.
    Useful for assessing a company's financial position.
    """
    if USE_FINANCIAL_DATASETS:
        params = _create_params(ticker, period, limit, report_period_gt, report_period_gte, report_period_lt, report_period_lte)
        data = call_api("/financials/balance-sheets/", params)
        return data.get("balance_sheets", {})
    else:
        # Use yfinance
        return get_yf_balance_sheet(ticker, period, limit)

@tool(args_schema=FinancialStatementsInput)
def get_cash_flow_statements(
    ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int = 10,
    report_period_gt: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period_lt: Optional[str] = None,
    report_period_lte: Optional[str] = None
) -> dict:
    """
    Retrieves a company's cash flow statements,
    showing how cash is generated and used across
    operating, investing, and financing activities.
    Useful for understanding a company's liquidity and solvency.
    """
    if USE_FINANCIAL_DATASETS:
        params = _create_params(ticker, period, limit, report_period_gt, report_period_gte, report_period_lt, report_period_lte)
        data = call_api("/financials/cash-flow-statements/", params)
        return data.get("cash_flow_statements", {})
    else:
        # Use yfinance
        return get_yf_cash_flow(ticker, period, limit)
