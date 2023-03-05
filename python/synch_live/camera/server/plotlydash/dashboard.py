import dash
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd

from .layout import html_layout

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
    )

    # Load dataframe
    df = pd.read_csv('./synch_live/camera/SynchLivehello.csv')

    # Custom HTML layout
    dash_app.index_string = html_layout
    
    # Create Layout
    dash_app.layout = html.Div(
        children=[
            dcc.Graph(
                id="histogram-graph",
                figure=px.scatter(df, x='position_x', y='position_y', animation_frame='frame_id'
                    , animation_group="player_id"
                    , size_max=55
                    , range_x=[0,1]
                    , range_y=[0,1])
                ,
            )
        ],
        id="dash-container",
    )
    return dash_app.server

def create_data_table(df):
    """Create Dash datatable from Pandas DataFrame."""
    table = dash_table.DataTable(
        id="database-table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        sort_action="native",
        sort_mode="native",
        page_size=300,
    )
    return table