import plotly


def get_candles(data, title):
    """
    This function plots the prices of a given asset
    :param data: DataFrame of prices
    :param title: Title of the plot
    :return:
    """

    # Create the plotly figure
    fig = plotly.graph_objects.Figure()

    # Add the candlestick trace
    fig.add_trace(plotly.graph_objects.Candlestick(x=data.index,
                                                   open=data["o"],
                                                   high=data["h"],
                                                   low=data["l"],
                                                   close=data["c"],
                                                   name="Candlesticks"))

    # Add the titles
    fig.update_layout(title=title,
                      yaxis_title="Price",
                      xaxis_title="Date")

    # Show the figure
    fig.show()

    return fig
