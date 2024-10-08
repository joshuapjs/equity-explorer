import os
import re
import multiprocessing
from threading import Timer
import webbrowser
from dash import Dash, dcc, html, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly
from . import visualize as viz
from . import fundamental_ratios as fr
from . import quant_ratios as qr
from .price_data import Asset


# NOTE: Change this if your key is not stored in an Environment Variable.
key = os.getenv("API_Polygon")

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])  # Instantiating the basis for the Dash App

# Setting up the predefined elements offered by Dash
app.layout = html.Div([
    # Header of the Application
    html.Div(children="Equity Explorer",
             style={"fontSize": "24px",
                    'color': 'white',
                    'fontFamily': 'Arial',
                    }),

    html.Div(style={'height': '20px'}),
    # Search field for the tickers that should be analyzed
    dcc.Input(id="ticker_as_text".format("search"),
              value="AAPL".format("search"), style={"margin-left": "15px"}),
    # Search button to confirm the input
    dbc.Button('Submit', id='search_button', color='#101010', style={'backgroundColor': '#101010',
                                                                     'color': 'white',
                                                                     'fontFamily': 'Arial',
                                                                     'border': '1px solid #636efa',
                                                                     'marginLeft': '1.0em'
                                                                     }),
    html.Div(style={'height': '20px'}),
    # Container to align the two graphs in a row
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


def add_table_row(ticker_symbol: str):
    """
    Calculates parameters of a row for the DataTable.
    :param ticker_symbol: This calculates the parameters for each stock given ticker_symbol concurrently.
    :return: Returns a dictionary that will be appended to a list to be recognized as a row of a DataTable.
    """
    # Feeding the POD with its values.
    stock = fr.Stock(key, ticker_symbol)
    
    # Setting up the object to distribute the data.
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    # NOTE: For each parameter displayed in a column a task is created. The measures can be modified but their function
    # have to return a dictionary (see output of function in fr). It is also necessary to adjust the placeholder data at
    # the top so that all datapoints are allocated correctly. Each new measures have to work with:
    # multiprocessing.Manager().manager.dict().
    tasks = [fr.ep_ratio, fr.pb_ratio, fr.current_ratio,
             fr.ro_equity, fr.ro_assets, fr.div_growth]

    # Each Process is added to jobs to call join() on them and awaiting their result.
    jobs = []
    for task in tasks:
        process_for_task = multiprocessing.Process(target=task, args=(stock, return_dict))
        jobs.append(process_for_task)
        process_for_task.start()
    
    # Calling join() on each process to wait until they are finished.
    for process in jobs:
        process.join()
    
    # Preparation of the data for the output.
    calculated_ratios = return_dict.values()

    row_of_data = {}
    for item in calculated_ratios:
        row_of_data.update(item)

    # We must not forget the Ticker_symbol of the row!
    row_of_data.update({"Ticker": ticker_symbol})

    return row_of_data


@callback(Output("ratio_table", "data"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_ratio_table(n_clicks, ticker):
    data = []
    ticker_list = re.findall(r'[A-Z0-9]*\.?[A-Z0-9]*', ticker)  
    clean_ticker_list = [element for element in ticker_list if element != '']
    
    # Creating multiple functions or only one.
    for current_ticker in clean_ticker_list:
        data.append(add_table_row(current_ticker))

    return data


@callback(Output("quant_table", "data"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_quant_table(n_clicks, ticker):
    data = []

    # Function to add a row to the DataTable for each ticker
    def add_row(ticker_symbol):
        capm_values = qr.get_capm(key, ticker_symbol)

        row = {"Ticker": ticker_symbol,
                        "Alpha": round(capm_values[0], 3),
                        "Beta": round(capm_values[1], 3),
                        "Volatility": round(qr.get_realized_volatility(key, ticker_symbol), 3),
                        "Sharpe ratio": round(qr.get_sharpe_ratio(key, ticker_symbol), 3)}

        return row
    
    # Find all tickers in the input string.
    ticker_list = re.findall(r'[A-Z0-9]*\.?[A-Z0-9]*',ticker)
    clean_ticker_list = [element for element in ticker_list if element != '']
    
    # Call the function for each element given in the input string.
    for current_ticker in clean_ticker_list:
        data.append(add_row(current_ticker))

    return data


@callback(Output("price_line", "figure"),
          Input("search_button", "n_clicks"),
          State("ticker_as_text", "value"))
def update_graph(n_clicks, ticker):

    # Function to add a line to the Graph for each ticker
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
    # Find all tickers in the input string.
    ticker_list = re.findall(r'[A-Z0-9]*\.?[A-Z0-9]*', ticker)
    clean_ticker_list = [element for element in ticker_list if element != '']
    
    for symbol in clean_ticker_list:
        data = (Asset(key, symbol, "Stock", start=start_date).get_prices()
                .pct_change(periods=1)
                .dropna())

        data["c"] = (1 + data["c"]).cumprod() - 1
        add_graph_line(symbol, data, fig)

    fig.update_layout(title="Returns")

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
    ticker_list = re.findall(r'[A-Z0-9]*\.?[A-Z0-9]*', ticker)
    clean_ticker_list = [element for element in ticker_list if element != '']
    first_hist_data = (fr.Stock(key, clean_ticker_list[0]).get_prices()
                       .pct_change(periods=1)
                       .dropna())
    
    fig = viz.get_histogram(first_hist_data, clean_ticker_list[0])
    clean_ticker_list.remove(clean_ticker_list[0])

    for symbol in clean_ticker_list:
        data = (fr.Stock(key, symbol).get_prices()
                .pct_change(periods=1)
                .dropna())

        add_hist_trace(symbol, data, fig)

    fig.update_layout(title="Distribution")

    return fig


if __name__ == "__main__":
    def open_browser(debug=True):
        webbrowser.open_new('http://127.0.0.1:8050')
    Timer(1, open_browser).start()
    app.run()
