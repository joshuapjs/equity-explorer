"""
All values in this module will be stored in memory using redis, to offer a fast way to reuse the data.
The logic within redis is as follows:

    stock_ticker + "_" + value_type

    - stock_ticker: The ticker symbol of the stock.
    - value_type: The kind of data requested. Through this Module it is possible to request "fundamentals", "ticker_info" and "dividends".

The values are stored as pickle elements which is in general a dependency of this module and will be transformed to Pandas-DataFrames.
A subscription for the Polygon.io Stocks-Starter is necessary to request the data.
"""

import subprocess
import atexit
import json
import time
import os
import pickle
import pandas as pd
import requests
import redis


def handle_response(response, asset_ticker, client_error_message, show=False):
    """
    This function handles the response from the API.
    :param response: The response from the API.
    :param asset_ticker: The ticker of the asset.
    :param client_error_message: The message to display if the client made an error.
    :return: The response in JSON format.
    """

    data = None

    if str(response.status_code)[0] == "4" or response.json()["results"] == []:
        raise Exception(f"{client_error_message} for {asset_ticker}")
    elif str(response.status_code)[0] == "2":
        data = response.json()
        if show: print(json.dumps(response.json(), sort_keys=True, indent=4))
    elif str(response.status_code)[0] == "5":
        raise Exception("Internal server error, please try again later")

    return data


# TODO Make the API Calls asynchronous.
def get_fundamentals(api_key, asset_ticker="AAPL", show=False, aggregate=False, statement_type="balance_sheet"):
    """
    This function retrieves the fundamentals of a given asset.
    :param api_key: The API key for Polygon.io.
    :param asset_ticker: (Default value = "AAPL") The ticker of the asset.
    :param show: (Default value = False) Print the response to the console.
    :param aggregate: (Default value = False) Aggregate the statements by statement type.
    :param statement_type: (Default value = "balance_sheet") The type of statement to aggregate.
    :return: Dictionary of the following form -> (ticker, filing_date, number) : statement_df.
    """

    # Url to request the data from Polygon.io.
    url = (f"https://api.polygon.io/vX/reference/financials?ticker="
           f"{asset_ticker}"
           f"&apiKey={api_key}")
    
    # Request the data from Polygon.io.
    response = requests.get(url)

    # Ensure to handle cases where no data is avaible properly. 
    data = handle_response(response, asset_ticker, "No fundamentals found", show=show)["results"]

    all_statements = {}
    # Iterate through the filings and the statements in each filing.
    for number in range(0,len(data)):
        for statement in data[number]["financials"].keys():
            
            # Get the reporting period to categorize the statement - period is stored in a Tuple.
            reporting_period = (data[number]["start_date"], data[number]["start_date"]) 

            # Get the statement and convert it to a DataFrame with the provided "order" as the index.
            raw_statement = data[number]["financials"][statement]
            statement_df = pd.DataFrame(raw_statement)
            statement_df = statement_df.transpose()
            # statement_df["order"] = statement_df["order"].astype(int)
            # TODO This might not be necessary in my test the column was already filled with int.
            #      However, if it creates problems the respective line can be uncommented.
            statement_df = statement_df.set_index(["order", "label"])
            statement_df.sort_index(inplace=True)

            # Add the statement to the dictionary with the key being the tuple (ticker, reporting_period, statement).
            all_statements[(asset_ticker, reporting_period, statement)] = statement_df

    # Aggregate the statements by statement type.
    if aggregate:
        aggregated_statements = {}
        aggregated_index = []
        for statement in all_statements.keys():

            if statement[2] == "balance_sheet" and statement_type == "balance_sheet":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

            elif statement[2] == "income_statement" and statement_type == "income_statement":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

            elif statement[2] == "cash_flow_statement" and statement_type == "cash_flow_statement":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

            elif statement[2] == "comprehensive_income" and statement_type == "comprehensive_income":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

        actual_index = pd.MultiIndex.from_tuples(aggregated_index)  # Create a MultiIndex from the list of tuples.

        for key, value in aggregated_statements.items():
            value = value.reindex(actual_index, fill_value=0)  # Fill missing values with 0.
            aggregated_statements[key] = value["value"].to_list()

        all_statements = pd.DataFrame(aggregated_statements, index=actual_index)
        all_statements.sort_index(axis=1, inplace=True, ascending=False)

    return all_statements


def get_ticker_info(api_key, asset_ticker="AAPL", show=False):
    """
    This function is used, to return info about a given ticker.
    :param api_key: The API-Key for Polygon.io.
    :param asset_ticker: The stock ticker.
    :return: A DataFrame containing the info about a given stock.
    """
    
    # Request the data from Polygon.io.
    url = f"https://api.polygon.io/v3/reference/tickers/{asset_ticker}?apiKey={api_key}"
    response = requests.get(url)
    
    # Handle the response give by Polygon.io.
    info = handle_response(response, asset_ticker, "No information found", show=show)
    info_df = pd.DataFrame(info)["results"]  # First declaring and then filtering the dataframe is the correct order here.

    return info_df


def get_dividends(api_key, ticker="AAPL", show=False):
    """
    This function is used, to return the dividends of a stock.
    :param api_key: The API-Key for Polygon.io.
    :param ticker: The stock ticker.
    :return: A DataFrame containing the dividends of a given stock.
    """
    
    # Request the data from Polygon.io.
    url = f"https://api.polygon.io/v3/reference/dividends?ticker={ticker}&apiKey={api_key}"
    response = requests.get(url)

    data = handle_response(response, ticker, "No dividends found", show=show)["results"]
    dividends_df = pd.DataFrame(data)  # First filtering for "results" then declaring the df is correct order here.

    return dividends_df
