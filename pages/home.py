import dash_html_components as html
import dash_core_components as dcc
from utils import Header, make_dash_table
import pandas as pd
import pathlib

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

def create_layout(app):
	return html.Div(
		[
			html.Div([Header(app)]),
			
		],
		className="page",
	)
		