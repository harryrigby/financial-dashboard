# Importing the required libraries
import pandas as pd
import yfinance as yf
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import dash.dash_table as dt

def analytics_page(TICKERS, TIME_PERIODS):
    return html.Div([

        # Company name
        html.H2(id="company-name"),

        # Company industry
        html.H4(html.I(id="industry-name")),

        # Company information
        html.Div(id="company-info"),
        html.Div(style={"height": "20px"}),

        # Company financials
        dt.DataTable(
            id="financials-table",
            columns=[
                {"name": "Metric", "id": "Metric"},
                {"name": "Value", "id": "Value"}
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "10px"},
            style_header={"fontWeight": "bold"},
            data = [
                {"Metric": "Latest Close Price ($)", "Value": 0},
                {"Metric": "Market Cap ($Bn)", "Value": 0},
                {"Metric": "52 Week High ($)", "Value": 0},
                {"Metric": "52 Week Low ($)", "Value": 0},
                {"Metric": "Dividend Yield (5 year average)", "Value": 0},
                {"Metric": "Price/Earnings Ratio (TTM)", "Value": 0},
                {"Metric": "Earnings per Share (TTM)", "Value": 0},
            ]
        ),

        # Stock price chart
        html.Div(style={"height": "20px"}),
        html.H3("Stock Price and Returns Charts:", style={'margin-top': '20px'}),

        # Time period dropdown
        html.Label("Select a time period:", style={'margin-top': '20px'}),
        dcc.Dropdown(
            id="time-period-dropdown",
            options=[{"label": period, "value": period} for period in TIME_PERIODS.keys()],
            value="1 Year",  # Default value
            clearable=False,
        ),

        # Price and % change
        html.Div(style={"height": "20px"}),
        html.H3(id="price"),

        # Plot chart
        dcc.Graph(id="stock-price-graph"),

        # Market & industry correlation
        dt.DataTable(
            id="correlation",
            columns=[
                {"name": "Metric", "id": "Metric"},
                {"name": "Value", "id": "Value"}
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "10px"},
            style_header={"fontWeight": "bold"},
            data = [
                {"Metric": "Beta (5 year monthly)", "Value": 0},
                {"Metric": "Correlation with market index", "Value": 0},
                {"Metric": "Correlation with industry index", "Value": 0},
            ]
        ),

        # Stock returns chart
        html.Div(style={"height": "20px"}),
        dcc.Graph(id='stock-returns-graph'),

        # Stock returns histogram
        dcc.Graph(id='returns-histogram'),

        # Tables for statistics and risk analysis
        html.H3("Descriptive Statistics:", style={'margin-top': '20px'}),
        dt.DataTable(
            id="stats-table",
            columns=[
                {"name": "Metric", "id": "Metric"},
                {"name": "Chosen Stock", "id": "Value"},
                {"name": "Industry Average", "id": "Industry Average"},
                {"name": "S&P 500", "id": "S&P 500"}
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "10px"},
            style_header={"fontWeight": "bold"},
            data=[  # Placeholder for stats
                {"Metric": "Mean", "Value": "N/A", "Industry Average": "N/A", "S&P 500": "N/A"},
                {"Metric": "Median", "Value": "N/A", "Industry Average": "N/A", "S&P 500": "N/A"},
                {"Metric": "Min", "Value": "N/A", "Industry Average": "N/A", "S&P 500": "N/A"},
                {"Metric": "Max", "Value": "N/A", "Industry Average": "N/A", "S&P 500": "N/A"},
                {"Metric": "25th Percentile", "Value": "N/A", "Industry Average": "N/A", "S&P 500": "N/A"},
                {"Metric": "75th Percentile", "Value": "N/A", "Industry Average": "N/A", "S&P 500": "N/A"}
        ]
        ),

        html.Div(style={"height": "20px"}),

        html.H3("Risk Metrics:", style={'margin-top': '20px'}),
        dt.DataTable(
            id="risk-table",
            columns=[
                {"name": "Metric", "id": "Metric"},
                {"name": "Chosen Stock", "id": "Value"}
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "10px"},
            style_header={"fontWeight": "bold"},
            data=[  # Placeholder for stats
                {"Metric": "Volatility"},
                {"Metric": "Beta"},
                {"Metric": "R-squared"},
                {"Metric": "Sharpe Ratio"},
                {"Metric": "Sortino Ratio"},
                {"Metric": "Treynor Ratio"},
                {"Metric": "Value at Risk (VaR)"},
                {"Metric": "Expected Shortfall (ES)"}
            ]
        ),
    ])

def strategies_page():
    return html.Div([
        html.H1('Stock Risk and Performance Analysis', style={'text-align': 'center', 'margin-bottom': '20px'}),
        html.P('This is a simple dashboard example built with Dash.'),
        html.P('You can add more functionality as needed!')
    ])