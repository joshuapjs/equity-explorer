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
        data = pd.DataFrame(response.json()["results"])
        numbers = data.index.to_list()
        all_statements = {}

        for number in numbers:
            for statement in pd.DataFrame(data.loc[number]).loc["financials"].loc[number].keys():

                filing_date = pd.DataFrame(data.loc[number]).loc["filing_date"].loc[number]

                raw_statement = pd.DataFrame(data.loc[number]).loc["financials"].loc[number][statement]
                statement_df = pd.DataFrame(raw_statement)
                statement_df = statement_df.transpose()
                statement_df["order"] = statement_df["order"].astype(int)
                statement_df = statement_df.set_index("order")
                statement_df.sort_index(inplace=True)

                all_statements[(self.asset_ticker, filing_date, statement)] = statement_df

        if show: print(json.dumps(response.json(), sort_keys=True, indent=4))

        return all_statements

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
