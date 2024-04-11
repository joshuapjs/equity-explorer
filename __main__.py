from dash import Dash, dcc, html, dash_table, callback, Output, Input, State
# from price_data import Asset
from . import price_data.Asset
import quant_ratios as qr
import fundamental_ratios as fr
import dash_bootstrap_components as dbc
import visualize as viz
import pandas as pd
import utils
import plotly
import os

key = os.getenv("API_Polygon")

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])  # Instantiating the basis for the Dash App
app.layout = html.Div([
    # header / name of the Application
    html.Div(children="Portfolio Stack",
             style={"fontSize": "24px",
                    'color': 'white',
                    'fontFamily': 'Arial',
                    }),

    html.Div(style={'height': '20px'}),
    # Search field for the tickers that should be analyzed
    dcc.Input(id="ticker_as_text".format("search"),
              value="AAPL".format("search")),
    # Search button to confirm the input
    dbc.Button('Submit', id='search_button', color='#101010', style={'backgroundColor': '#101010',
                                                                     'color': 'white',
                                                                     'fontFamily': 'Arial',
                                                                     'border': '1px solid #636efa'
                                                                     }),
    html.Div(style={'height': '20px'}),
    # Container containing the graphs align in a row
    dbc.Container([dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id="price_line")),
        dbc.Col(dcc.Graph(figure={}, id="price_hist")),
        html.Div(style={'height': '20px'}),
        # DataTable containing the fundamental ratios
        dash_table.DataTable(data=[{"Ticker": "AAPL",
                                    "E/P Ratio": "calculating.",
                                    "P/B Ratio": "calculating.",
                                    "Current Ratio": "calculating.",
                                    "ROE": "calculating.",
                                    "ROA": "calculating.",
                                    "Average Dividend growth": "calculating."}],
                             columns=[{"name": i, "id": i} for i in [
                                 "Ticker",
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
                                 'border': '1px solid #636efa'
                             },
                             style_header={
                                 'backgroundColor': '#101010',
                                 'color': 'white',
                                 'fontWeight': 'bold',
                                 'borderBottom': '1px solid #636efa',
                                 'padding': '5px'
                             },
                             style_cell={
                                 'backgroundColor': '#101010',
                                 'color': 'white',
                                 'fontFamily': 'Arial',
                                 'fontSize': 14,
                                 'border': '1px solid #636efa',
                                 'padding': '5px'
                             }),
        html.Div(style={'height': '20px'}),
        # DataTable containing the quantitative ratios
        dash_table.DataTable(data=[{"Ticker": "AAPL",
                                    "Alpha": "calculating.",
                                    "Beta": "calculating.",
                                    "Volatility": "calculating.",
                                    "Sharpe ratio": "calculating."}],
                             columns=[{"name": i, "id": i} for i in [
                                 "Ticker",
                                 "Alpha",
                                 "Beta",
                                 "Volatility",
                                 "Sharpe ratio"]],
                             page_size=6,
                             id="quant_table",
                             style_as_list_view=True,
                             style_table={
                                 'overflowX': 'auto',
                                 'border': '1px solid #636efa'
                             },
                             style_header={
                                 'backgroundColor': '#101010',
                                 'color': 'white',
                                 'fontWeight': 'bold',
                                 'borderBottom': '1px solid #636efa',
                                 'padding': '5px'
                             },
                             style_cell={
                                 'backgroundColor': '#101010',
                                 'color': 'white',
                                 'fontFamily': 'Arial',
                                 'fontSize': 14,
                                 'border': '1px solid #636efa',
                                 'padding': '5px'
                             }),
        html.Div(style={'height': '20px'}),
    ])], fluid=True)])


@callback(Output("ratio_table", "data"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_ratio_table(n_clicks, ticker):
    data = []

    # function to fetch the data needed for each ratio
    def fetch_value(object_method, default_value):
        try:
            return object_method()
        except Exception as e:
            print(e)
            return default_value

    # function to add a line to the DataTable for each ticker
    def add_line(ticker_symbol):

        stock = fr.Stock(key, ticker_symbol)

        line_of_data = {"Ticker": ticker_symbol,
                        "E/P Ratio": fetch_value(stock.ep_ratio, pd.NA),
                        "P/B Ratio": fetch_value(stock.pb_ratio, pd.NA),
                        "Current Ratio": fetch_value(stock.current_ratio, pd.NA),
                        "ROE": fetch_value(stock.ro_equity, pd.NA),
                        "ROA": fetch_value(stock.ro_assets, pd.NA),
                        "Average Dividend growth": fetch_value(stock.div_growth, pd.NA)}

        data.append(line_of_data)

    # Detecting if only one company of multiple tickers were requested
    utils.process_table_data(ticker, add_line)

    return data


@callback(Output("quant_table", "data"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_quant_table(n_clicks, ticker):
    data = []

    # function to add a line to the DataTable for each ticker
    def add_line(ticker_symbol):

        capm_values = qr.get_capm(key, ticker_symbol)

        line_of_data = {"Ticker": ticker_symbol,
                        "Alpha": round(capm_values[0], 3),
                        "Beta": round(capm_values[1], 3),
                        "Volatility": round(qr.get_realized_volatility(key, ticker_symbol), 3),
                        "Sharpe ratio": round(qr.get_sharpe_ratio(key, ticker_symbol), 3)}

        data.append(line_of_data)

    utils.process_table_data(ticker, add_line)

    return data


@callback(Output("price_line", "figure"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_graph(n_clicks, ticker):

    # function to add a line to the Graph for each ticker
    def add_graph_line(ticker_symbol, data, figure):
        figure.add_trace(plotly.graph_objects.Scatter(x=data.index,
                                                      y=data["c"],
                                                      name=ticker_symbol))

    spx = Asset(key, "SPX", "Indices")
    spx_position = spx.get_prices()
    spx_returns = spx_position.pct_change(periods=1).dropna()
    spx_returns["c"] = (1 + spx_returns["c"]).cumprod() - 1
    start_date = spx_returns.index.to_list()[0].strftime('%Y-%m-%d')

    fig = viz.get_line(spx_returns, "SPX")

    # Detecting if only one company of multiple tickers were requested
    if "," in ticker:
        symbol_list = ticker.strip().split(",")

        for symbol in symbol_list:
            data = (Asset(key, symbol, "Stock", start=start_date).get_prices()
                    .pct_change(periods=1)
                    .dropna())

            data["c"] = (1 + data["c"]).cumprod() - 1
            add_graph_line(symbol, data, fig)

        fig.update_layout(title="Returns")
    else:
        data = (Asset(key, ticker, "Stock", start=start_date).get_prices()
                .pct_change(periods=1)
                .dropna())

        data["c"] = (1 + data["c"]).cumprod() - 1
        add_graph_line(ticker, data, fig)

    fig = fig.update_layout(yaxis_title="Returns")

    return fig


@callback(Output("price_hist", "figure"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_hist(n_clicks, ticker):

    # Function to add additional data to the histogram
    def add_hist_trace(ticker_symbol, data, figure):
        figure.add_trace(plotly.graph_objects.Histogram(x=data["c"],
                                                        y=data["c"],
                                                        name=ticker_symbol,
                                                        opacity=0.7))

    # Detecting if only one company of multiple tickers were requested
    if "," in ticker:
        symbol_list = ticker.strip().split(",")
        first_hist_data = (fr.Stock(key, symbol_list[0]).get_prices()
                           .pct_change(periods=1)
                           .dropna())
        fig = viz.get_histogram(first_hist_data, symbol_list[0])
        symbol_list.remove(symbol_list[0])

        for symbol in symbol_list:
            data = (fr.Stock(key, symbol).get_prices()
                    .pct_change(periods=1)
                    .dropna())

            add_hist_trace(symbol, data, fig)

        fig.update_layout(title="Distribution")

    else:
        data = (fr.Stock(key, ticker).get_prices()
                .pct_change(periods=1)
                .dropna())

        fig = viz.get_histogram(data, ticker)

    return fig


if __name__ == "__main__":
    app.run(debug=True)
