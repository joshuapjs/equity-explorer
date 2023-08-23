from data import Asset
from fundamentals import get_dividends
from scipy.stats import gmean
import datetime as dt


class Stock(Asset):

    def __init__(self, api_key, asset_ticker, asset_class):
        super().__init__(api_key, asset_ticker, asset_class)

    def ep_ratio(self):
        """
        This function calculates the PE ratio of a stock
        :return:
        """
        self.start = (dt.datetime.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")
        self.end = dt.datetime.today().strftime("%Y-%m-%d")

        fundamentals = self.get_fundamentals(statement_type="income_statement")

        filings_dates = fundamentals.columns
        current_years_filings = [date for date in filings_dates if str(dt.datetime.today().year) in str(date)]

        if 4 > len(current_years_filings) > 0:
            missing_values = [(4 - int(len(current_years_filings))) * current_years_filings[0]]
            current_years_filings = current_years_filings + missing_values

        elif len(current_years_filings) == 0:
            current_years_filings = [date for date in filings_dates
                                     if str(dt.datetime.today() - dt.timedelta(days=100)) in str(date)]

        eps = fundamentals[current_years_filings].loc[(4200, "Basic Earnings Per Share")].to_list()
        summed_eps = sum(eps)

        price = self.get_prices()["c"][-1]

        try:
            pe_ratio = summed_eps / price
            return round(pe_ratio, 2)
        except ZeroDivisionError:
            return None

    def pb_ratio(self):

        self.start = (dt.datetime.today() - dt.timedelta(days=2)).strftime("%Y-%m-%d")
        self.end = (dt.datetime.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")

        equity = self.get_fundamentals(statement_type="balance_sheet").loc[(1400, "Equity")][0]
        shares = self.get_stock_infos()["weighted_shares_outstanding"]
        price = self.get_prices()["c"][-1]

        try:
            pb_ratio = price / (equity / shares)
            return round(pb_ratio, 2)
        except ZeroDivisionError:
            return None

    def current_ratio(self):

        assets = self.get_fundamentals(statement_type="balance_sheet").loc[(100, "Assets")][0]
        liabilities = self.get_fundamentals(statement_type="balance_sheet").loc[(600, "Liabilities")][0]

        try:
            pb_ratio = assets / liabilities
            return round(pb_ratio, 2)
        except ZeroDivisionError:
            return None

    def ro_equity(self):

        equity = self.get_fundamentals(statement_type="balance_sheet").loc[(1400, "Equity")][0]
        income = self.get_fundamentals(statement_type="income_statement").loc[(3200, "Net Income/Loss")][0]

        try:
            roe = income / equity
            return round(roe, 2)
        except ZeroDivisionError:
            return None

    def ro_assets(self):

        assets = self.get_fundamentals(statement_type="balance_sheet").loc[(100, "Assets")][0]
        income = self.get_fundamentals(statement_type="income_statement").loc[(3200, "Net Income/Loss")][0]

        try:
            roa = income / assets
            return round(roa, 2)
        except ZeroDivisionError:
            return None

    def div_growth(self):

        dividends = get_dividends(api_key=self.api_key, ticker=self.asset_ticker)
        dividends_growth = dividends["cash_amount"][::-1].pct_change(periods=1).dropna()
        average_dividends = gmean([rate + 1 for rate in dividends_growth.to_list()]) - 1

        return average_dividends
