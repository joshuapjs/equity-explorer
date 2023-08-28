from dash import Dash, dcc, html, dash_table, callback, Output, Input, State
import financial_ratios as fr
import dash_bootstrap_components as dbc
import visualizing as viz
import pandas as pd
import os

key = os.getenv("API_Polygon")
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([
    html.Div(children="Portfolio Stack",
             style={"fontSize": "24px"}),
    html.Div(style={'height': '20px'}),
    dcc.Input(id="ticker_as_text".format("search"),
              value="AAPL".format("search")),
    dbc.Button('Submit', id='search_button', color="dark"),
    html.Div(style={'height': '20px'}),
    dbc.Container([dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id="price_line")),
        dbc.Col(dcc.Graph(figure={}, id="price_hist")),
        html.Div(style={'height': '20px'}),
        dash_table.DataTable(data=[{"E/P Ratio": "calculating.",
                                    "P/B Ratio": "calculating.",
                                    "Current Ratio": "calculating.",
                                    "ROE": "calculating.",
                                    "ROA": "calculating.",
                                    "Average Dividend growth": "calculating."}],
                             columns=[{"name": i, "id": i} for i in [
                                 "E/P Ratio",
                                 "P/B Ratio",
                                 "Current Ratio",
                                 "ROE",
                                 "ROA",
                                 "Average Dividend growth"]],
                             page_size=6,
                             id="ratio_table",
                             style_as_list_view=True,
                             style_table={
                                 'overflowX': 'auto',
                                 'border': 'black'},
                             style_header={
                                 'backgroundColor': 'rgb(30, 30, 30)',
                                 'color': 'white'},
                             style_cell={
                                 'backgroundColor': 'rgb(50, 50, 50)',
                                 'color': 'white',
                                 'fontFamily': 'Arial',
                                 'fontSize': 14}),
        html.Div(style={'height': '20px'}),
    ])])])


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


@callback(Output("price_line", "figure"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_graph(n_clicks, ticker):

    data = (fr.Stock(key, ticker, "Stock").get_prices()
            .pct_change(periods=1)
            .dropna()
            .cumsum())

    fig = viz.get_line(data, str(ticker))
    fig = fig.update_layout(yaxis_title="Returns")

    return fig


@callback(Output("price_hist", "figure"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_hist(n_clicks, ticker):

    data = (fr.Stock(key, ticker, "Stock").get_prices()
            .pct_change(periods=1)
            .dropna())

    fig = viz.get_histogram(data, str(ticker))

    return fig


if __name__ == "__main__":
    app.run(debug=True)
