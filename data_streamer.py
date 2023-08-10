import requests
import os


api_key = os.getenv("API_Polygon")
currency_aggs_url = ("https://api.polygon.io/v2/aggs/ticker/"
                     "C:pair/range/1/day/start_date/end_date")


class DataStreamer:
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def get_data(self):
        key_string = '?sort=asc&apiKey=' + str(self.key)
        response = requests.get(self.url + key_string)
        return response.json()
