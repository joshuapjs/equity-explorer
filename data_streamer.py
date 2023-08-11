import pandas as pd
import requests
import json
import os


api_key = os.getenv("API_Polygon")
currency_aggs_url = ("https://api.polygon.io/v2/aggs/ticker/"
                     "C:pair/range/1/day/start_date/end_date")


class DataStreamer:

    api_key = os.getenv("API_Polygon")

    def __init__(self, asset_ticker, asset_class, start, end, frequency="day"):
        self.asset_ticker = asset_ticker
        self.asset_class = asset_class
        self.start = start
        self.end = end
        self.frequency = frequency

    def get_prices(self):
        asset_classes = {"Stock": self.get_stock_data,
                         "Option": self.get_options_data,
                         "Indices": self.get_indices_data,
                         "Forex": self.get_forex_data
                         }

        response = asset_classes[self.asset_class]()

        data = pd.DataFrame(json.loads(response)["results"])

        return data

    def get_stock_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={api_key}")

        response = requests.get(url)

        return response.text

    def get_options_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/O:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={api_key}")

        response = requests.get(url)

        return response.text

    def get_indices_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/I:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"sort=asc&limit=120&apiKey={api_key}")

        response = requests.get(url)

        return response.text


    def get_forex_data(self):
        url = (f"https://api.polygon.io/v2/aggs/ticker/C:{self.asset_ticker}"
               f"/range/1/{self.frequency}"
               f"/{self.start}/{self.end}?"
               f"adjusted=true&sort=asc&limit=120&apiKey={api_key}")

        print(url)

        response = requests.get(url)

        return response.text
