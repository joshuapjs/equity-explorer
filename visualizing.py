import plotly


def pretty_plot(func):
    def set_parameters(*args, **kwargs):
        plotly.io.templates.default = "plotly_dark"
        return func(*args, **kwargs)

    return set_parameters


@pretty_plot
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
                      xaxis_title="Date",
                      )

    return fig


@pretty_plot
def get_line(data, title):
    """
    This function plots the prices of a given asset
    :param data: DataFrame of prices
    :param title: Title of the plot
    :return:
    """

    # Create the plotly figure
    fig = plotly.graph_objects.Figure()

    # Add the candlestick trace
    fig.add_trace(plotly.graph_objects.Scatter(x=data.index,
                                               y=data["c"],
                                               name="Price"))

    # Add the titles
    fig.update_layout(title=title,
                      yaxis_title="Price",
                      xaxis_title="Date",
                      )

    return fig


@pretty_plot
def get_histogram(data, title):
    """
    This function plots the prices of a given asset
    :param data: DataFrame of prices
    :param title: Title of the plot
    :return:
    """

    # Create the plotly figure
    fig = plotly.graph_objects.Figure()

    # Add the candlestick trace
    fig.add_trace(plotly.graph_objects.Histogram(x=data["c"],
                                               y=data["c"],
                                               name="Price"))

    # Add the titles
    fig.update_layout(title=title,
                      yaxis_title="Count",
                      xaxis_title="Price",
                      )

    return fig
