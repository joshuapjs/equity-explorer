import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import os


api_key = os.getenv("API_Polygon")


class DataStream:

    api_key = os.getenv("API_Polygon")

    def __init__(self, asset_ticker, asset_class, start=datetime.today(),
                 end= datetime.today() - timedelta(days=7), frequency="day"):
        self.asset_ticker = asset_ticker
        self.asset_class = asset_class
        self.start = start
        self.end = end
        self.frequency = frequency

    def get_prices(self, show=False):

        asset_classes = {"Stock": self._get_stock_data,
                         "Option": self._get_options_data,
                         "Indices": self._get_indices_data,
                         "Forex": self._get_forex_data
                         }

        response = asset_classes[self.asset_class]()

        data = pd.DataFrame(json.loads(response)["results"])
        if show: print(data)

        return data


    def get_fundamentals(self, show=False):
        url = (f"https://api.polygon.io/vX/reference/financials?ticker="
               f"{self.asset_ticker}"
               f"&apiKey={api_key}")

        response = requests.get(url)
        print(response.json())
        data = pd.DataFrame(response.json()["results"])
        numbers =  data.index.to_list()
        all_statements = []

        print(pd.DataFrame(data.loc[0]).loc["financials"].loc[0])

        for number in numbers:
            for statement in pd.DataFrame(data.loc[number]).loc["financials"].keys():
                all_statements.append(pd.DataFrame(data.loc[number]).loc["financials"].loc[number])

        #all_statements = [[pd.DataFrame(data[number]["financials"][statement]) for statement in pd.DataFrame(data[number]["financials"]).index.to_list()] for number in numbers]
        if show: print(json.dumps(response.json(), sort_keys=True, indent=4))

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

print(DataStream(asset_ticker="TSLA", asset_class="Stock").get_fundamentals())


