# Importing the required libraries
import pandas as pd
import yfinance as yf
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import dash.dash_table as dt

def strategies_page():
    return html.Div([
        html.H1('Stock Risk and Performance Analysis', style={'text-align': 'center', 'margin-bottom': '20px'}),
        html.P('This is a simple dashboard example built with Dash.'),
        html.P('You can add more functionality as needed!')
    ])