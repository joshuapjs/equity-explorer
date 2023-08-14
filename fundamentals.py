import pandas as pd
import requests
import json


def get_fundamentals(api_key, ticker="AAPL", show=False, aggregate=False, statement_type="balance_sheet"):
    """
    This function retrieves the fundamentals of a given asset
    :param api_key: The API key for Polygon.io
    :param ticker: (Default value = "AAPL") The ticker of the asset
    :param show: (Default value = False) Print the response to the console
    :param aggregate: (Default value = False) Aggregate the statements by statement type
    :param statement_type: (Default value = "balance_sheet") The type of statement to aggregate
    :return: Dictionary of the following form -> (ticker, filing_date, number) : statement_df
    """
    url = (f"https://api.polygon.io/vX/reference/financials?ticker="
           f"{ticker}"
           f"&apiKey={api_key}")

    response = requests.get(url)
    data = pd.DataFrame(response.json()["results"])
    # Get the index of the filings to iterate through them later
    numbers = data.index.to_list()
    all_statements = {}

    # Iterate through the filings and the statements in each filing
    for number in numbers:
        for statement in pd.DataFrame(data.loc[number]).loc["financials"].loc[number].keys():

            filing_date = pd.DataFrame(data.loc[number]).loc["filing_date"].loc[number]

            # Get the statement and convert it to a DataFrame with the order as the index
            raw_statement = pd.DataFrame(data.loc[number]).loc["financials"].loc[number][statement]
            statement_df = pd.DataFrame(raw_statement)
            statement_df = statement_df.transpose()
            statement_df["order"] = statement_df["order"].astype(int)
            statement_df = statement_df.set_index(["order", "label"])
            statement_df.sort_index(inplace=True)

            # Add the statement to the dictionary with the key being the tuple (ticker, filing_date, statement)
            all_statements[(ticker, filing_date, statement)] = statement_df

    if show: print(json.dumps(response.json(), sort_keys=True, indent=4))

    # Aggregate the statements by statement type
    if aggregate:
        aggregated_statements = {}
        aggregated_index = []
        for statement in all_statements.keys():

            if statement[2] == "balance_sheet" and statement_type == "balance_sheet":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

            elif statement[2] == "income_statement" and statement_type == "income_statement":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

            elif statement[2] == "cash_flow_statement" and statement_type == "cash_flow_statement":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

            elif statement[2] == "comprehensive_income" and statement_type == "comprehensive_income":
                aggregated_statements[statement[1]] = all_statements[statement][["value"]]
                index = all_statements[statement].index.to_list()
                if len(aggregated_index) < len(index):
                    aggregated_index = index

        actual_index = pd.MultiIndex.from_tuples(aggregated_index)  # Create a MultiIndex from the list of tuples

        for key, value in aggregated_statements.items():
            value = value.reindex(actual_index, fill_value=0)  # Fill missing values with 0
            aggregated_statements[key] = value["value"].to_list()

        all_statements = pd.DataFrame(aggregated_statements, index=actual_index)
        all_statements.sort_index(axis=1, inplace=True, ascending=False)

    return all_statements
