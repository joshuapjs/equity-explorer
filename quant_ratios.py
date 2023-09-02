import statsmodels.api as sm
from price_data import Asset
import os

key = os.environ.get("API_Polygon")


def get_capm(api_key, asset_ticker):

    asset = Asset(api_key, asset_ticker, "Stock")
    asset_prices = asset.get_prices()["c"]
    asset_returns = asset_prices.pct_change(periods=1).dropna()

    spy = Asset(api_key, "SPX", "Indices")
    spy_prices = spy.get_prices()["c"]
    spy_returns = spy_prices.pct_change(periods=1).dropna()

    spy_returns = sm.add_constant(spy_returns)
    model = sm.OLS(asset_returns, spy_returns).fit()

    return model.summary()


def get_volatility(api_key, asset_ticker, freq=1):
    asset = Asset(api_key, asset_ticker, "Stock")
    asset_prices = asset.get_prices()["c"]
    asset_returns = asset_prices.pct_change(periods=freq).dropna()
    return asset_returns.std()
