from datetime import datetime, timedelta
import numpy as np
import statsmodels.api as sm
import pandas as pd
from .price_data import Asset


def get_capm(api_key, asset_ticker, freq=1):
    """
    Function to fetch the alpha and beta value for give ticker.
    :param api_key: key for the Polygon.io API
    :param asset_ticker: ticker as a string
    :param freq: frequency over how many periods the returns should be calculated
    :return: list with alpha and beta value
    """

    asset = Asset(api_key, asset_ticker, "Stock")

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

    return model.params


def get_realized_volatility(api_key, asset_ticker, freq=1):
    """
    Calculate the realized volatility for the last 365 days including weekends and holidays for the given ticker.
    :param api_key: key for the Polygon.io API
    :param asset_ticker: ticker as a string
    :param freq: frequency over how many periods the returns should be calculated
    :return: scalar value of the realized volatility
    """
    asset = Asset(api_key, asset_ticker, "Stock",
                  start=(datetime.today() - timedelta(days=360)).strftime('%Y-%m-%d'))  # 1 Year realized volatility
    asset_prices = asset.get_prices()["c"]
    asset_returns = asset_prices.pct_change(periods=freq).dropna()

    return asset_returns.std() * np.sqrt(252)  # TODO Does it really make sense to normalize the volatility with sqrt(252) ?


def get_sharpe_ratio(api_key, assert_ticker, risk_free_rate=0.0538):
    """
    Calculate the current sharpe ratio of the given ticker
    :param risk_free_rate: 53 Weeks T-Bill rate as of 2023-09-05
    :param api_key: key for the Polygon.io API
    :param assert_ticker: ticker as a string
    :return: scalar value of the sharpe ratio
    """
    asset = Asset(api_key, assert_ticker, "Stock",
                  start=(datetime.today() - timedelta(days=360)).strftime('%Y-%m-%d'))
    asset_prices = asset.get_prices()["c"].to_list()
    asset_return = (asset_prices[-1] - asset_prices[0]) / asset_prices[0]
    asset_volatility = get_realized_volatility(api_key, assert_ticker)
    sharpe_ratio = (asset_return - risk_free_rate) / asset_volatility

    return sharpe_ratio
