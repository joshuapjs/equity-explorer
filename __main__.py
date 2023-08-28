from dash import Dash, dcc, html, dash_table, callback, Output, Input, State
import financial_ratios as fr
import dash_bootstrap_components as dbc
import pandas as pd
import os

key = os.getenv("API_Polygon")
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.Div(children="Portfolio Stack"),
    html.Hr(),
    dcc.Input(id="ticker_as_text".format("search"),
              value="AAPL".format("search")),
    html.Button('Submit', id='search_button'),
    dash_table.DataTable(data=[],
                         columns=[{"name": i, "id": i} for i in [
                            "E/P Ratio",
                            "P/B Ratio",
                            "Current Ratio",
                            "ROE",
                            "ROA",
                            "Average Dividend growth"]],
                         page_size=6,
                         id="ratio_table"),
])


@callback(Output("ratio_table", "data"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_table(n_clicks, ticker):

    stock = fr.Stock(key, ticker, "Stock")

    def fetch_value(object_method, default_value):
        try:
            return object_method()
        except Exception as e:
            print(e)
            return default_value

    data = [{"E/P Ratio": fetch_value(stock.ep_ratio, pd.NA),
             "P/B Ratio": fetch_value(stock.pb_ratio, pd.NA),
             "Current Ratio": fetch_value(stock.current_ratio, pd.NA),
             "ROE": fetch_value(stock.ro_equity, pd.NA),
             "ROA": fetch_value(stock.ro_assets, pd.NA),
             "Average Dividend growth": fetch_value(stock.div_growth, pd.NA)}]

    return data


if __name__ == "__main__":
    app.run(debug=True)
