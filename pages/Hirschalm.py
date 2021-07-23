import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import pathlib
from utils import Header, make_dash_table
from dash.dependencies import Input, Output

def create_layout(app):
	return html.Div(
		[
			Header(app),
			html.Div(
				[
                    html.Div(
                        [
                            html.H4("Hirschalm page", className = "subtitle"),
                            html.H6("Select Challenge", className = "subtitle"),
                            dcc.Dropdown(id='Hir_dropdown',
                                options=[
                                    {'label': 'The First Turns', 'value': 'The First Turns'},
                                    {'label': 'The Little Adventure', 'value': 'The Little Adventure'},
                                    {'label': 'The Offpist Trail', 'value': 'The Offpist Trail'},
                                ],
                                value = 'The First Turns',
                                style = {"width": "50%"},
                            )
                        ]
                    )
				],
			),
            html.H6(["Top ten scores"]),
            dash_table.DataTable(
                id='hirtable')
            
		],
	)
 

		
		
