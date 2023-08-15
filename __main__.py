import visualizing as viz
import data_stream as ds
import os

key = os.getenv("API_Polygon")

viz.get_candles(ds.DataStream(key, "AAPL", "Stock", start="2022-01-01", end="2022-12-31").get_prices(), "AAPL Prices")
