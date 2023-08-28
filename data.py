import pandas as pd
from datetime import datetime, timedelta
import fundamentals as f
import requests
import json


class Asset:
    """
    This class is used to retrieve data from the Polygon.io API
    """

    def __init__(self, api_key, asset_ticker, asset_class,
                 start=(datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
                 end=datetime.today().strftime('%Y-%m-%d'), frequency="day"):

        self.api_key = api_key
        self.asset_ticker = asset_ticker
        self.asset_class = asset_class
        self.start = start
        self.end = end
        self.frequency = frequency

    def get_fundamentals(self, show=False, aggregate=True, statement_type="balance_sheet"):
        fundamentals = f.get_fundamentals(self.api_key,
                                          ticker=self.asset_ticker,
                                          show=show,
                                          aggregate=aggregate,
                                          statement_type=statement_type)

        return fundamentals

    def get_stock_infos(self, show=False):
        infos = f.get_ticker_info(api_key=self.api_key,
                                  ticker=self.asset_ticker,
                                  show=show)

        return infos

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
               f"adjusted=true&sort=asc&limit=120&apiKey={self.api_key}")

        response = requests.get(url)

        return response.text

    def _get_options_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/O:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={self.api_key}")

        response = requests.get(url)

        return response.text

    def _get_indices_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/I:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"sort=asc&limit=120&apiKey={self.api_key}")

        response = requests.get(url)

        return response.text

    def _get_forex_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/C:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={self.api_key}")

        response = requests.get(url)

        return response.text
