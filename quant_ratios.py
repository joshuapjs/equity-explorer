from datetime import datetime, timedelta
import numpy as np
import statsmodels.api as sm
import pandas as pd
from price_data import Asset
import os

key = os.environ.get("API_Polygon")


def get_capm(api_key, asset_ticker, freq=1):

    asset = Asset(api_key, asset_ticker, "Stock",
                  start=(datetime.today() - timedelta(days=720)).strftime('%Y-%m-%d'))

    asset_prices = asset.get_prices()["c"]
    asset_prices.rename(asset_ticker, inplace=True)
    asset_returns = asset_prices.pct_change(periods=1).dropna()
    asset_returns.index = asset_returns.index.normalize()

    spx = Asset(api_key, "SPX", "Indices")
    spx_position = spx.get_prices()["c"]
    spx_position.rename("SPX", inplace=True)
    spx_returns = spx_position.pct_change(periods=freq).dropna()
    spx_returns.index = spx_returns.index.normalize()

    concatenated_returns = pd.concat([asset_returns, spx_returns], axis=1).dropna()

    market_portfolio = sm.add_constant(concatenated_returns["SPX"])
    stock_returns = concatenated_returns[asset_ticker]
    model = sm.OLS(stock_returns, market_portfolio).fit()

    return model.summary()


def get_realized_volatility(api_key, asset_ticker, freq=1):
    asset = Asset(api_key, asset_ticker, "Stock",
                  start=(datetime.today() - timedelta(days=360)).strftime('%Y-%m-%d'))  # 1 Year realized volatility
    asset_prices = asset.get_prices()["c"]
    asset_returns = asset_prices.pct_change(periods=freq).dropna()
    return asset_returns.std() * np.sqrt(252)


def get_sharpe_ratio(api_key, assert_ticker):
    asset = Asset(api_key, assert_ticker, "Stock",
                  start=(datetime.today() - timedelta(days=252)).strftime('%Y-%m-%d'))
    asset_prices = asset.get_prices()["c"].to_list()
    asset_return = (asset_prices[-1] - asset_prices[0]) / asset_prices[0]
    asset_volatility = get_realized_volatility(api_key, assert_ticker)
    risk_free_rate = 0.0538  # 53 Weeks T-Bill rate as of 2023-09-05
    sharpe_ratio = (asset_return - risk_free_rate) / asset_volatility

    return sharpe_ratio