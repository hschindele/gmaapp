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
                  
def makearchiverecords():
    armountainlist = []
    for mountain in mountains_list:
        curdf = archive190.copy()
        curdf = curdf[curdf['Mountain'] == mountain]
        curdf = curdf[(curdf['chaltype'] == 'Airtime') | (curdf['chaltype'] == 'Open Trick') | (curdf['chaltype'] == 'Gated Trick') | (curdf['chaltype'] == 'Triple Drop') | (curdf['chaltype'] == 'Long Jump') | (curdf['chaltype'] == 'Single Drop') | (curdf['chaltype'] == 'Single Trick')]
        curdf = curdf[curdf['Was WR'] == True]
        curdf = curdf.groupby('challenge name', group_keys=False).apply(lambda x: x.loc[x.score.idxmax()])
        curdf = curdf.rename(columns={'challenge name':'Challenge Name','Name':'Player','score':'Score','Timestamp':'Date Set'})
        column_names = ['Challenge Name','Score','Player','Date Set','OS','chaltype','type','Mountain','Was WR','Verified?','Link']
        curdf = curdf.reindex(columns=column_names)
        curdt = dt.DataTable(
            id='archivetable',
            columns=[{'name':i, 'id':i} for i in curdf],
            css=[{'selector': ".show-hide", "rule": "display: none"}],
            data=curdf.to_dict('rows'),
            style_cell_conditional=[
                {
                    'if': {'column_id': 'Challenge Name'},
                    'textAlign': 'left'
                },
                {
                    'if': {'column_id': 'Score'},
                    'textAlign': 'center'
                },
                {
                    'if': {'column_id': 'OS'},
                    'textAlign': 'center'
                },
                {
                    'if': {'column_id': 'Player'},
                    'textAlign': 'center'
                }
            ],
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Single Trick"'
                    },
                    'backgroundColor': '#deabd8'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Single Drop"'
                    },
                    'backgroundColor': '#deabd8'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Airtime"'
                    },
                    'backgroundColor': '#deabd8'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Long Jump"'
                    },
                    'backgroundColor': '#deabd8'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Gated Trick"'
                    },
                    'backgroundColor': '#fe7198'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Open Trick"'
                    },
                    'backgroundColor': '#ffa162'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Triple Drop"'
                    },
                    'backgroundColor': '#55c8ba'
                }
            ],
            hidden_columns=['chaltype','type','Mountain','Was WR','Verified?','Link']
        )
        armountainlist.append(curdt)
    return armountainlist

mountainwrlist = makearchiverecords()

def archivepage(outtype):
    if outtype == 'one':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3("v190 World Records"),
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
                    html.Div("Version 191 introduced balance changes that significantly nerfed certain competitive exploits. Notably, hop extends, combo multipliers on rails, and drift boosts. These changes resulted in a complete wipe of all trick, drop, and airtime challenges. Here you can view the pre-190 world records and scores for the tracks affected. Many of these scores are much higher than what would be possible today.")
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
            dbc.Col([
                html.Div(id='archive-content')
            ],
            style={'width': '50%'})
        ])
    ],
    style = {'padding-left':20})
])
