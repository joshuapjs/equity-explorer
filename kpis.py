from data import Asset
import datetime as dt


class Stock(Asset):

    def __init__(self, api_key, asset_ticker, asset_class):
        super().__init__(api_key, asset_ticker, asset_class)

    def pe_ratio(self):
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
            pe_ratio = price / summed_eps
            return round(pe_ratio, 2)
        except ZeroDivisionError:
            return None
