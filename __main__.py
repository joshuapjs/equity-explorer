from dash import Dash, dcc, html, dash_table, callback, Output, Input
from financial_ratios import Stock
import dash_bootstrap_components as dbc
import os

key = os.getenv("API_Polygon")
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

Stock = Stock(key, "AAPL")

app.layout = html.Div([
    html.Div(children="Portfolio Stack"),
    html.Hr(),
    dcc.RadioItems(options=['AAPL', 'TSLA', 'AMZN'], value='AAPL', id='ticker_as_text'),
    dash_table.DataTable(data=[{"E/P Ratio": 0,
                               "P/B Ratio": 0,
                               "Current Ratio": 0,
                               "ROE": 0,
                               "ROA": 0,
                               "Average Dividend growth": 0,
                               }],
                         columns=[{"name": i, "id": i} for i in [
                             "E/P Ratio",
                             "P/B Ratio",
                             "Current Ratio",
                             "ROE",
                             "ROA",
                             "Average Dividend growth"]], page_size=6)
])


if __name__ == "__main__":
    app.run(debug=True)