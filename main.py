# Importing the required libraries
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import dash.dash_table as dt

# Importing pages
from overview import analytics_page
from risk_and_performance import strategies_page
from forecasts import forecasts_page

# Initialising the app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Obtain information on S&P 500 companies
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
table = pd.read_html(url)
tickers_df = table[0]
TICKERS = tickers_df['Symbol'].tolist()
company_info = tickers_df.set_index("Symbol").to_dict(orient="index")
        
# Define availible time periods
TIME_PERIODS = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "10 Years": "10y",
    "YTD": "ytd",
    "Max": "max"
}

# Defining the dashboard layout
app.layout = html.Div([
    html.H1("S&P 500 Company Analytics Dashboard", style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Ticker dropdown
    html.H3("Select ticker:", style={'margin-top': '20px'}),
    dcc.Dropdown(
            id="ticker-dropdown",
            options=[{"label": ticker, "value": ticker} for ticker in TICKERS],
            value=TICKERS[0],  # Default value
            clearable=False,
    ),

    html.Div(style={"height": "20px"}),

    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Overview', value='tab-1'),
        dcc.Tab(label='Risk & Performance', value='tab-2'),
        dcc.Tab(label='Forecasts', value='tab-3'),
    ]),
    html.Div(id='tabs-content')
])

# Callback to change tabs
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-example', 'value')
)
def render_page(tab):
    if tab == 'tab-1':
        return analytics_page(TICKERS, TIME_PERIODS) 
    elif tab == 'tab-2':
        return strategies_page()
    elif tab == 'tab-3':
        return forecasts_page()


# Callback to update the stock price graph
@app.callback(
    [Output("stock-price-graph", "figure"),
     Output("stock-returns-graph", "figure"),
     Output("company-info", "children"),
     Output("stats-table", "data"),
     Output("financials-table", "data"),
     Output("company-name", "children"),
     Output("correlation", "data"),
     Output("industry-name", "children"),
     Output("price", "children"),
     Output("returns-histogram", "figure")],
    [Input("ticker-dropdown", "value"),
     Input("time-period-dropdown", "value")]
)
def update_graph(ticker, time_period):
    try:
        # Map the time period to Yahoo Finance format
        yf_period = TIME_PERIODS.get(time_period, "6mo")  # Default to 6 months

        # Get stock data
        stock_data = yf.download(ticker, period=yf_period)
        stock_data["Returns"] = 100 * (stock_data["Close"] - stock_data["Close"].shift(1)) / stock_data["Close"].shift(1)
        
        # Get market data
        market_data = yf.download("^GSPC", period=yf_period)
        market_data["S&P 500 relative price"] = market_data["Close"]/market_data["Close"].iloc[0]
        market_data["S&P 500 relative price"] = market_data["S&P 500 relative price"]*float(stock_data["Close"].iloc[0])
        market_data["Returns"] = 100 * (market_data["Close"] - market_data["Close"].shift(1)) / market_data["Close"].shift(1)

        # Get industry data
        def get_industry_index(ticker):
            industry = company_info.get(ticker)["GICS Sector"]

            industry_data = None

            if industry == 'Industrials':
                industry_data = yf.download("XLI", period=yf_period)
            elif industry == 'Health Care':
                industry_data = yf.download("XLV", period=yf_period)
            elif industry == 'Information Technology':
                industry_data = yf.download("XLK", period=yf_period)
            elif industry == 'Utilities':
                industry_data = yf.download("XLU", period=yf_period)
            elif industry == 'Financials':
                industry_data = yf.download("XLF", period=yf_period)
            elif industry == 'Materials':
                industry_data = yf.download("XLB", period=yf_period)
            elif industry == 'Consumer Discretionary':
                industry_data = yf.download("XLY", period=yf_period)
            elif industry == 'Real Estate':
                industry_data = yf.download("XLRE", period=yf_period)
            elif industry == 'Communication Services':
                industry_data = yf.download("XLC", period=yf_period)
            elif industry == 'Consumer Staples':
                industry_data = yf.download("XLP", period=yf_period)
            elif industry == 'Energy':
                industry_data = yf.download("XLE", period=yf_period)

            return industry_data

        industry_data = get_industry_index(ticker)
        industry_data["Industry index relative price"] = industry_data["Close"]/industry_data["Close"].iloc[0]
        industry_data["Industry index relative price"] = industry_data["Industry index relative price"]*float(stock_data["Close"].iloc[0])
        industry_data["Returns"] = 100*(industry_data["Close"] - industry_data["Close"].shift(1)) / industry_data["Close"].shift(1)
        
        if stock_data.empty:
            return (
                px.line(title="No data available"),
                px.line(title="No data available")
            )
        
        # Price chart
        fig_price = px.line(
            pd.concat([stock_data["Close"], market_data["S&P 500 relative price"], industry_data["Industry index relative price"]]),
            labels={"Date": "Date", "value": "Close Price (USD)"}
        )
        
        # Returns chart
        fig_returns = px.line(
            stock_data["Returns"],
            labels={"Date": "Date", "value": "Returns (%)"}
        )

        # Histogram
        fig_returns_histogram = go.Figure(
            data=go.Histogram(x=stock_data["Returns"], nbinsx=30)
        )

        # Company information
        ticker = ticker.upper()  # Ensure the ticker is uppercase for lookup
        def get_description(ticker):
            return yf.Ticker(ticker).info['longBusinessSummary']
        
        if ticker in company_info:
            info = company_info[ticker]
            company_details = get_description(ticker)
        else:
            company_details = "No company information available for this ticker."

        # Descriptive statistics of the chosen stock
        stock_stats = stock_data["Returns"].describe()
        industry_stats = industry_data["Returns"].describe()
        market_stats = market_data["Returns"].describe()

        stats_data = [
            {"Metric": "Mean daily return", "Value": f"{stock_stats["mean"]:.2f}%", "Industry Average": f"{industry_stats["mean"]:.2f}%", "S&P 500": f"{market_stats["mean"]:.2f}%"},
            {"Metric": "Median daily return", "Value": f"{stock_stats["50%"]:.2f}%", "Industry Average": f"{industry_stats["50%"]:.2f}%", "S&P 500": f"{market_stats["50%"]:.2f}%"},
            {"Metric": "Largest day-on-day loss", "Value": f"{stock_stats["min"]:.2f}%", "Industry Average": f"{industry_stats["min"]:.2f}%", "S&P 500": f"{market_stats["min"]:.2f}%"},
            {"Metric": "Largest day-on-day gain", "Value": f"{stock_stats["max"]:.2f}%", "Industry Average": f"{industry_stats["max"]:.2f}%", "S&P 500": f"{market_stats["max"]:.2f}%"},
            {"Metric": "25th Percentile", "Value": f"{stock_stats["25%"]:.2f}%", "Industry Average": f"{industry_stats["25%"]:.2f}%", "S&P 500": f"{market_stats["25%"]:.2f}%"},
            {"Metric": "75th Percentile", "Value": f"{stock_stats["75%"]:.2f}%", "Industry Average": f"{industry_stats["75%"]:.2f}%", "S&P 500": f"{market_stats["75%"]:.2f}%"}
        ]
        
        # Company financials
        def get_key_metrics(ticker):

            # Downloading prices and ticker info
            prices = yf.download(ticker, period="1y")
            ticker_info = yf.Ticker(ticker).info

            # 0: Latest close price (number indicates index)
            last_close = float(round(prices["Close"][ticker].iloc[-1], 2)) if not prices.empty else None

            # 1, 2: 52 week high/low
            year_high = round(ticker_info['fiftyTwoWeekHigh'], 2) if 'fiftyTwoWeekHigh' in ticker_info else None
            year_low = round(ticker_info['fiftyTwoWeekLow'], 2) if 'fiftyTwoWeekLow' in ticker_info else None

            # 3: Market cap
            mkt_cap = round(ticker_info['marketCap']/1e9, 2) if 'marketCap' in ticker_info else None

            # 4: Dividend yield
            div_yield = round(ticker_info['fiveYearAvgDividendYield'], 2) if 'fiveYearAvgDividendYield' in ticker_info else "--"

            # 5: PE ratio
            PE_ratio = round(ticker_info['trailingPE'], 2) if 'trailingPE' in ticker_info else None

            # 6: Earnings per share
            EPS = round(ticker_info['trailingEps'], 2) if 'trailingEps' in ticker_info else None

            # 7. Beta
            beta = ticker_info['beta'] if 'beta' in ticker_info else "N/A"

            return last_close, year_high, year_low, mkt_cap, div_yield, PE_ratio, EPS, beta

        key_metrics = get_key_metrics(ticker)

        financials = [
            {"Metric": "Latest Close Price ($)", "Value": key_metrics[0]},
            {"Metric": "Market Cap ($Bn)", "Value": key_metrics[3]},
            {"Metric": "52 Week High ($)", "Value": key_metrics[1]},
            {"Metric": "52 Week Low ($)", "Value": key_metrics[2]},
            {"Metric": "Dividend Yield (5 year average)", "Value": key_metrics[4]},
            {"Metric": "Price/Earnings Ratio (TTM)", "Value": key_metrics[5]},
            {"Metric": "Earnings per Share (TTM)", "Value": key_metrics[6]}
        ]

        # Name & industry
        company_name = company_info.get(ticker)["Security"]
        company_industry = company_info.get(ticker)["GICS Sector"]

        # Price correlations
        market_correlation = round(float(pd.merge_asof(stock_data["Close"], market_data["Close"], left_index=True, right_index=True, direction='nearest').corr().loc[ticker].iloc[1]), 3)
        industry_correlation = round(float(pd.merge_asof(stock_data["Close"], industry_data["Close"], left_index=True, right_index=True, direction='nearest').corr().loc[ticker].iloc[1]), 3)
        beta = key_metrics[7]
        correlations = [
            {"Metric": "Beta (5 year monthly)", "Value": beta},
            {"Metric": "Correlation with market index", "Value": market_correlation},
            {"Metric": "Correlation with industry index", "Value": industry_correlation}
        ]

        # Price & returns
        start_price = stock_data["Close"].iloc[0]
        end_price = stock_data["Close"].iloc[-1]
        period_rets = 100*(end_price-start_price)/start_price
        end_date = stock_data.index[-1].date()
        price_rets = f"Latest close: ${float(round(end_price, 2))} ({float(round(period_rets, 2))}%) on {end_date}"

        return fig_price, fig_returns, company_details, stats_data, financials, company_name, correlations, company_industry, price_rets, fig_returns_histogram

    except Exception as e:
        return (
            px.line(title=f"Error: {str(e)}"),
            px.line(title=f"Error: {str(e)}"),
            f"Error fetching company information: {str(e)}",
            [], # Return empty table in case of error
            [],
            f"Error fetching company name: {str(e)}",
            [],
            f"Error fetching company industry: {str(e)}",
            0.00,
            px.line(title=f"Error: {str(e)}")
        )

# Run the dashbaord
if __name__ == "__main__":
    app.run_server(debug=True)
