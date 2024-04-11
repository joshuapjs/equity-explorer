"""
This is just a module to aggregate code that belongs to different modules but has no clear space within the program.
"""


def process_table_data(asset_ticker_s, func):

    if "," in asset_ticker_s:
        ticker_list = asset_ticker_s.strip().split(",")

        func(ticker_list[0])
        ticker_list.remove(ticker_list[0])

        for ticker in ticker_list:
            func(ticker)
    else:
        func(asset_ticker_s)
