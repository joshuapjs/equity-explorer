import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import os


api_key = os.getenv("API_Polygon")


class DataStream:
    """
    This class is used to retrieve data from the Polygon.io API
    """

    api_key = os.getenv("API_Polygon")

    def __init__(self, asset_ticker, asset_class, start=(datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
                 end=datetime.today().strftime('%Y-%m-%d'), frequency="day"):

        self.asset_ticker = asset_ticker
        self.asset_class = asset_class
        self.start = start
        self.end = end
        self.frequency = frequency

    def get_fundamentals(self, show=False):
        """
        This function retrieves the fundamentals of a given asset
        :param show: (Default value = False) Print the response to the console
        :return: Dictionary of the following form -> (ticker, filing_date, number) : statement_df
        """
        url = (f"https://api.polygon.io/vX/reference/financials?ticker="
               f"{self.asset_ticker}"
               f"&apiKey={api_key}")

        response = requests.get(url)
        data = pd.DataFrame(response.json()["results"])
        # Get the index of the filings to iterate through them later
        numbers = data.index.to_list()
        all_statements = {}

        # Iterate through the filings and the statements in each filing
        for number in numbers:
            for statement in pd.DataFrame(data.loc[number]).loc["financials"].loc[number].keys():

                filing_date = pd.DataFrame(data.loc[number]).loc["filing_date"].loc[number]

                # Get the statement and convert it to a DataFrame with the order as the index
                raw_statement = pd.DataFrame(data.loc[number]).loc["financials"].loc[number][statement]
                statement_df = pd.DataFrame(raw_statement)
                statement_df = statement_df.transpose()
                statement_df["order"] = statement_df["order"].astype(int)
                statement_df = statement_df.set_index("order")
                statement_df.sort_index(inplace=True)

                # Add the statement to the dictionary with the key being the tuple (ticker, filing_date, statement)
                all_statements[(self.asset_ticker, filing_date, statement)] = statement_df

        if show: print(json.dumps(response.json(), sort_keys=True, indent=4))

        return all_statements

    def get_prices(self, show=False):
        """
        This function retrieves the prices of a given asset
        :param show: (Default value = False) Print the response to the console
        :return:
        """

        # Create a dictionary of functions to call based on the asset class
        asset_classes = {"Stock": self._get_stock_data,
                         "Option": self._get_options_data,
                         "Indices": self._get_indices_data,
                         "Forex": self._get_forex_data
                         }

        # Call the appropriate function based on the asset class
        response = asset_classes[self.asset_class]()

        # Convert the response to a DataFrame
        data = pd.DataFrame(json.loads(response)["results"])
        data["t"] = data["t"].apply(lambda x: pd.to_datetime(x, unit="ms"))  # Convert the timestamp to pandas datetime
        data = data.set_index("t")  # Set the index to the timestamp
        data.sort_index(inplace=True)
        if show: print(data)

        return data

    def _get_stock_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={api_key}")

        response = requests.get(url)

        return response.text

    def _get_options_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/O:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={api_key}")

        response = requests.get(url)

        return response.text

    def _get_indices_data(self):

        assert self.asset_class == "Stock"

        url = (f"https://api.polygon.io/v2/aggs/ticker/I:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"sort=asc&limit=120&apiKey={api_key}")

        response = requests.get(url)

        return response.text

    def _get_forex_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/C:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={api_key}")

        print(url)

        response = requests.get(url)

        return response.text


# print(DataStream("AAPL", "Stock").get_fundamentals(show=True)) # Get the fundamentals of a stock
