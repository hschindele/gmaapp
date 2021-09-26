import dash  # (version 1.12.0)
import dash_table as dt
import pandas as pd
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from utils import Header, sidebar
from helpers import get_challenge_names, convertMillisNoHours, getchallengeImage
import pathlib

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

PATH = pathlib.Path(__file__)
DATA_PATH = PATH.joinpath("../data").resolve()
df = pd.read_csv(DATA_PATH.joinpath("out.csv"))
allwrs = pd.read_csv(DATA_PATH.joinpath("allwrs.csv"))
sortedwrs = pd.read_csv(DATA_PATH.joinpath("sortedwrs.csv"))
allpbs = pd.read_csv(DATA_PATH.joinpath("allpbs.csv"))
ttwrs = pd.read_csv(DATA_PATH.joinpath("ttwrs.csv"))
challenges = pd.read_csv(DATA_PATH.joinpath("gmachallenges.csv"))
archive190 = pd.read_csv(DATA_PATH.joinpath("gma190archive.csv"))

mountains_list = ['Hirschalm', 'Waldtal', 'Elnakka', 'Dalarna', 'Rotkamm', 'Saint Luvette',
                  'Passo Grolla', 'Ben Ailig', 'Mount Fairview', 'Pinecone Peaks']
                  
mountainwrlist = [1,2,3,4,5,6,7,8,9,10]

def archivepage(outtype):
    if outtype != 'one':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(returnstring+" World Records"),
                    html.Br(),
                    html.H4('Hirschalm 🇦🇹', className='title'),
                    html.Hr(),
                    mountainwrlist[0],
                    html.Br(),
                    html.H4('Waldtal 🇩🇪'),
                    html.Hr(),
                    mountainwrlist[1],
                    html.Br(),
                    html.H4('Elnakka 🇫🇮'),
                    html.Hr(),
                    mountainwrlist[2],
                    html.Br(),
                    html.H4('Dalarna 🇸🇪'),
                    html.Hr(),
                    mountainwrlist[3],
                    html.Br(),
                    html.H4('Rotkamm 🇨🇭'),
                    html.Hr(),
                    mountainwrlist[4],
                    html.Br(),
                    html.H4('Saint Luvette 🇫🇷'),
                    html.Hr(),
                    mountainwrlist[5],
                    html.Br(),
                    html.H4('Passo Grolla 🇮🇹'),
                    html.Hr(),
                    mountainwrlist[6],
                    html.Br(),
                    html.H4('Ben Ailig 🏴󠁧󠁢󠁳󠁣󠁴󠁿'),
                    html.Hr(),
                    mountainwrlist[7],
                    html.Br(),
                    html.H4('Mount Fairview 🇨🇦'),
                    html.Hr(),
                    mountainwrlist[8],
                    html.Br(),
                    html.H4('Pinecone Peaks 🇺🇸'),
                    html.Hr(),
                    mountainwrlist[9],
                        ],
                    style={'margin-left':15}
                    ),
                ])
            ])
    else:
        return
        
archive_layout = html.Div([
    Header(app),
    dbc.Row([
        sidebar,
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.H3('v190 Archive'),
                    html.Hr(),
                    html.Br(),
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.H4('Archive Info',
                        style={'text-decoration':'underline'}
                    ),
                    html.Div("Version 191 introduced balance changes that significantly nerfed certian competative exploits. Notably, hop extends, combo multipliers on rails, and drift boosts. These changes resulted in a complete wipe of all trick, drop, and airtime challenges. Here you can view the pre-190 world records and scores for the tracks affected. Many of these scores are much higher than what would be possible today.")
                ]),
                dbc.Col([
                    html.H4('Select View Type',
                        style={'text-decoration':'underline'}
                    ),
                    dcc.Dropdown(
                        id='archiveselect',
                        options=[
                            {'label':'World Records', 'value':'one'},
                            {'label':'Top 5', 'value':'five'},
                            {'label':'Top 10', 'value':'ten'},
                            {'label':'All Submissions', 'value':'all'},
                        ],
                        value='one',
                        searchable=False,
                        style = {'width': '70%'}
                    )
                ])
            ]),
            html.Br(),
            html.Hr(),
            html.Div(id='archive-content')
        ])
    ],
    style = {'padding-left':20})
])
