# equity-explorer

Please first have a look at the [Disclaimer](#Disclaimer).

Now that you are familiar how this application can be used, feel free to continue.  

The Portfolio-Stack was developed to support portfolio construction (of course without putting any capital at risk and only for educational purposes), powered by Polygon API. I intend to further maintain this Repo to expand its capabilities. 

# Features

Several different Tickers can be requested and their returns and several different KPIs can be compared. The period used for the calculation of the indicators is 1 year.

![4eaf7a6c-793d-4e9e-b6b6-24799e0536bd](https://github.com/joshuapjs/equity-explorer/assets/82243579/9eaaec17-694a-43d3-ba73-afa9bbf5ac76)

# Prerequisites

First and foremost an API Key to [Polygion.io](https://polygon.io) is needed, giving access to "Stocks Starter" and "Indices Starter" (or higher). Please visit [Pricing](https://polygon.io/pricing) for further details. I have no affiliation with Polygon.io, just excited what they have to offer. The "Indices Starter" can be avoided if the default request for the S&P 500, to be shown in the returns graph, is removed. As explained under [Setup](#Setup) the API Key should ideally be stored in an environment variable namend "API\_Polygon". 

A `.txt` file is included in the folder `env`, enabling the reproduction of my environment explained [here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#building-identical-conda-environments).

Briefly stated, a Python version of 3.11.4 or higher is recommended, as this version was used during the development. The following third-party libraries are also necessary:

- `dash`
- `dash_bootstrap_components`
- `pandas`
- `plotly`
- `scipy`
- `numpy`
- `statsmodels`

Many thanks to everyone in the open-source community for their hard work and contributions that make this and many other projects possible.

# Setup

- First, ideally recreate my Conda Environment with the explanatory resources mentioned above and the content in the `env` folder. 
- Besides the Environment there is some work to the with the API Key. The API-Key should be stored in an environment Variable named "API\_Polygon". How this exactly works depends on the System. An alternetive would be to modify the `key` variable in the `__main__.py` file.

# Usage

- If everything is setup, the application be executed through the command line or terminal through:
```shell
python -m equity-explorer
```
- The Web App will open in your browser. The Session can be closed (this is for the newbies) with `ctrl + c` through the terminal.
- You can enter Stock Tickers, separated by everything except capital letters and confirm by clicking on Submit.

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Disclaimer

The information provided by this dashboard is for informational purposes only and is not intended for trading or investment advice. All information is provided "as is" without warranty of any kind. Users should not rely on this information in making any investment decisions. Instead, users should consult with a qualified financial advisor to ensure that any investment decisions are based on comprehensive and tailored advice. We do not accept responsibility for any losses or damages arising from the use of this information. **Past performance is not indicative of future results**.
