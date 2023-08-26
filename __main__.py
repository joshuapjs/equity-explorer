from dash import Dash, dcc, html, dash_table, callback, Output, Input
import financial_ratios as fr
import dash_bootstrap_components as dbc
import os

key = os.getenv("API_Polygon")
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.Div(children="Portfolio Stack"),
    html.Hr(),
    dcc.RadioItems(options=['AAPL', 'TSLA', 'AMZN'], value='AAPL', id='ticker_as_text'),
    dash_table.DataTable(data=[],
                         columns=[],
                         page_size=6,
                         id="ratio_table"),
])


@callback(Output("ratio_table", "data"),
          Input("ticker_as_text", "value"))
def update_table(ticker):

    stock = fr.Stock(key, "AAPL", "Stock")

    data = [{"E/P Ratio": stock.ep_ratio(),
             "P/B Ratio": stock.pb_ratio(),
             "Current Ratio": stock.current_ratio(),
             "ROE": stock.ro_equity(),
             "ROA": stock.ro_assets(),
             "Average Dividend growth": stock.div_growth()}]

    columns = [{"name": i, "id": i} for i in [
        "E/P Ratio",
        "P/B Ratio",
        "Current Ratio",
        "ROE",
        "ROA",
        "Average Dividend growth"]]

    return data, columns


if __name__ == "__main__":
    app.run(debug=True)
