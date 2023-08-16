import visualizing as viz
import data_stream as ds
import os

key = os.getenv("API_Polygon")

viz.get_line(ds.DataStream(key, "AAPL", "Stock", start="2023-08-01", end="2023-08-16").get_prices(), "AAPL Prices")
