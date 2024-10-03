import datetime as dt
import pandas as pd
from scipy.stats import gmean
from .price_data import Asset
from .fundamental_data import get_dividends


# This class primarily works as a plain old data class.

# Background information: Initially it had all operations that were done with its data as methods. this was not an
# optimal architecture because methods can not be called asynchronously.
class Stock(Asset):

    def __init__(self, api_key, asset_ticker, asset_class="Stock"):
        super().__init__(api_key, asset_ticker, asset_class)


def ep_ratio(stock_class: Stock, concurrency_manager):
    """
    This function calculates the Earnings-Yield of a stock.
    
    stock_class: Stock class that stored all its specific data to make requests with.
    :return: Earnings-Yield or None.
    """
    # Setting the start and end date for the request. 
    start = (dt.datetime.today() - dt.timedelta(days=720)).strftime("%Y-%m-%d")
    end = dt.datetime.today().strftime("%Y-%m-%d")

    # Requesting the fundamental stock data.
    fundamentals = stock_class.get_fundamentals(statement_type="income_statement")

    # Fetching the filing dates of the current year. 
    #  TODO Idea: The file should fetch the most recent values not just from this year.
    filings_dates = fundamentals.columns

    # TODO Idea: This could be calculated more carefully. On this value a lot of metrics are based on.
    #      Current strategy is to use the values of the past year and this year.
    #      If there are more recent values this year the values from past year will be ignored.
    current_years_filings = [date for date in filings_dates if (
                str(dt.datetime.today().year - 1) in str(date) or str(dt.datetime.today().year) in str(date))]

    # Removing old values if they exist so that only the 4 most recent values are included in the calculation.
    if 4 < len(current_years_filings):
        # Calculating the last index of the relevant data
        lower_bound = 4 - len(current_years_filings)
        current_years_filings = current_years_filings[0:lower_bound]
    print(current_years_filings)
    # Getting the earnings of the list, that was cleaned above and summing up the earnings.
    eps = fundamentals[current_years_filings].loc[(4200, "Basic Earnings Per Share")].to_list()
    summed_eps = sum(eps)

    # Grabbing the current stock price.
    # TODO Idea: There could be a faster request for this.
    price = stock_class.get_prices()["c"][-1]

    # Calculate the actual calculation.
    try:
        stock_ep_ratio = summed_eps / price
        concurrency_manager["E/P Ratio"] = {"E/P Ratio": round(stock_ep_ratio, 4)}
        return round(stock_ep_ratio, 4)
    except ZeroDivisionError:
        concurrency_manager["E/P Ratio"] = {"E/P Ratio": pd.NA}
        return None


def pb_ratio(stock_class: Stock, concurrency_manager):
    """
    Calculate the Price-To-Book ratio.

    stock_class: Stock class that stored all its specific data to make requests with.
    :return: Price-To-Book-Ratio or None.
    """

    # Setting the start and end date for the request. 
    start = (dt.datetime.today() - dt.timedelta(days=5)).strftime("%Y-%m-%d")
    end = (dt.datetime.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")

    # Requesting the data that is needed for the calculation.
    equity = stock_class.get_fundamentals(statement_type="balance_sheet").loc[(1400, "Equity")][0]
    shares = stock_class.get_infos()["weighted_shares_outstanding"]
    price = stock_class.get_prices()["c"][-1]

    # Do the actual calculation.
    try:
        pb_ratio = price / (equity / shares)
        concurrency_manager["P/B Ratio"] = {"P/B Ratio": round(pb_ratio, 2)}
        return round(pb_ratio, 2)
    except ZeroDivisionError:
        concurrency_manager["P/B Ratio"] = {"P/B Ratio": pd.NA}
        return None


def current_ratio(stock_class: Stock, concurrency_manager):
    """
    Calculate the Current Ratio for a Stock.
    stock_class: Stock class that stored all its specific data to make requests with.
    :return: Price-To-Book-Ratio or None.
    """

    # Request the data needed.
    fundamental_data = stock_class.get_fundamentals(statement_type="balance_sheet")
    assets = fundamental_data.loc[(100, "Assets")][0]
    liabilities = fundamental_data.loc[(600, "Liabilities")][0]

    # Do the actual calculation.
    try:
        current_ratio = assets / liabilities
        concurrency_manager["Current Ratio"] = {"Current Ratio": round(current_ratio, 2)}
        return round(current_ratio, 2)
    except ZeroDivisionError:
        concurrency_manager["Current Ratio"] = {"Current Ratio": pd.NA}
        return None


def ro_equity(stock_class: Stock, concurrency_manager):
    """
    Calculate the Return-On-Equity for a given stock.

    stock_class: Stock class that stored all its specific data to make requests with.
    :return: Price-To-Book-Ratio or None.
    """

    # Request the data necessary. 
    equity = stock_class.get_fundamentals(statement_type="balance_sheet").loc[(1400, "Equity")][0]
    income = stock_class.get_fundamentals(statement_type="income_statement").loc[(3200, "Net Income/Loss")][0]

    # Do the actual calculation.
    try:
        roe = income / equity
        concurrency_manager["ROE"] = {"ROE": round(roe, 2)}
        return round(roe, 2)
    except ZeroDivisionError:
        concurrency_manager["ROE"] = {"ROE": pd.NA}
        return None


def ro_assets(stock_class: Stock, concurrency_manager):
    """
    Calculate the Return-On-Asset for a given stock.

    stock_class: Stock class that stored all its specific data to make requests with.
    :return: Price-To-Book-Ratio or None.
    """

    # Request the data necessary. 
    assets = stock_class.get_fundamentals(statement_type="balance_sheet").loc[(100, "Assets")][0]
    income = stock_class.get_fundamentals(statement_type="income_statement").loc[(3200, "Net Income/Loss")][0]

    # Do the actual calculation.
    try:
        roa = income / assets
        concurrency_manager["ROA"] = {"ROA": round(roa, 2)}
        return round(roa, 2)
    except ZeroDivisionError:
        concurrency_manager["ROA"] = {"ROA": pd.NA}
        return None


def div_growth(stock_class: Stock, concurrency_manager):
    """
    Calculate the Dividend Growth for a given Stock.
    
    stock_class: Stock class that stored all its specific data to make requests with.
    :return: Price-To-Book-Ratio or None.
    """

    # Request the data necessary. 
    dividends = get_dividends(api_key=stock_class.api_key, ticker=stock_class.asset_ticker)

    # Calculate the divided growth for all dividends.
    dividends_growth = dividends["cash_amount"][::-1].pct_change(periods=1).dropna()
    # Calculate the geometric average of the dividend growth.
    average_dividends = round(gmean([rate + 1 for rate in dividends_growth.to_list()]) - 1, 3)

    concurrency_manager["Average Dividend growth"] = {"Average Dividend growth": average_dividends}

    return average_dividends
