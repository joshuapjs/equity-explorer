import visualizing as viz
import data as ds
import os

key = os.getenv("API_Polygon")

ds.Asset(key, "AAPL", "Stock", start="2023-08-01", end="2023-08-16").get_fundamentals(show=True)
