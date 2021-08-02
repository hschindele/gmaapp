import dash  # (version 1.12.0)
import dash_table as dt
import pandas as pd
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import pathlib
from utils import Header, sidebar
from helpers import convertMillis

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../gmaapp/data").resolve()
sortedwrs = pd.read_csv(DATA_PATH.joinpath("sortedwrs.csv"))

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

allpbs = pd.read_csv(DATA_PATH.joinpath("allpbs.csv"))

mountains_list = ['Hirschalm', 'Waldtal', 'Elnakka', 'Dalarna', 'Rotkamm', 'Saint Luvette',
                  'Passo Grolla', 'Ben Ailig', 'Mount Fairview', 'Pinecone Peaks']
                  
totsumofbest = (sortedwrs[sortedwrs['type'] != 'High score'].score.sum())*1000

def makemountainWRs(sortedcopy, type):
    wrtables = []
    if type == 'timetrial':
        sortedcopy = sortedcopy[sortedcopy['type'] != 'High score']
    elif type == 'highscore':
        sortedcopy = sortedcopy[sortedcopy['type'] == 'High score']
    for mountain in mountains_list:
        mountaincopy = sortedcopy[sortedcopy['Mountain'] == mountain]
        wrdt = dt.DataTable(
            id='wrtable',
            columns=[{'name': i, 'id': i} for i in mountaincopy.columns],
            css=[{'selector': ".show-hide", "rule": "display: none"}],
            data=mountaincopy.to_dict('rows'),
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
                    'if': {'column_id': 'Duration'},
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
                        'filter_query': '{chaltype} eq "Race"'
                    },
                    'backgroundColor': '#6abe7c'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Trail"'
                    },
                    'backgroundColor': '#deabd8'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Slap"'
                    },
                    'backgroundColor': '#deabd8'
                },
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
                        'filter_query': '{chaltype} eq "TTB"'
                    },
                    'backgroundColor': '#9c6ab3'
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
                        'filter_query': '{chaltype} eq "Distance"'
                    },
                    'backgroundColor': '#4d9bd8'
                },
                {
                    'if': {
                        'filter_query': '{chaltype} eq "Triple Drop"'
                    },
                    'backgroundColor': '#55c8ba'
                }
            ],
            hidden_columns=['chaltype','type','Mountain']
        )
        wrtables.append(wrdt)
    return wrtables

def makemountainrankings(chaltype):
    retlist = []
    for mountain in mountains_list:
        mtnrankdf = allpbs.copy()
        titlestring = 'Overall'
        if chaltype == 'tt':
            mtnrankdf = mtnrankdf[mtnrankdf['type'] != 'High score']
            titlestring = 'TT'
        elif chaltype == 'hs':
            mtnrankdf = mtnrankdf[mtnrankdf['type'] == 'High score']
            titlestring = 'HS'
        totaltitlestring = mountain+' '+titlestring+' Rankings'
        returnrank = mtnrankdf[mtnrankdf['Mountain'] == mountain].groupby('Name')['Points'].sum().reset_index()
        returnrank = returnrank.sort_values('Points', ascending=False).reset_index(drop=True)
        returnrank.index = returnrank.index.set_names(['Rank'])
        rankdt = dt.DataTable(
            id='displayrankings',
            columns=[
                {'name': [totaltitlestring,'Name'], 'id': 'Name'},
                {'name': [totaltitlestring,'Points'], 'id': 'Points'}
            ],
            data=returnrank.to_dict('rows'),
            style_cell = {'text-align':'center'},
            merge_duplicate_headers=True
        )
        retlist.append(rankdt)
    return retlist
    
overallranks = makemountainrankings('')
ttranks = makemountainrankings('tt')
hsranks = makemountainrankings('hs')

def mountainrankpage(outtype):
    if outtype != 'timetrial' and outtype != 'highscore':
        return html.Div([
            html.H5('Hirschalm Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[0]
                ]),
                dbc.Col([
                    ttranks[0]
                ]),
                dbc.Col([
                    hsranks[0]
                ])
            ]),
            html.Br(),
            html.H5('Waldtal Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[1]
                ]),
                dbc.Col([
                    ttranks[1]
                ]),
                dbc.Col([
                    hsranks[1]
                ])
            ]),
            html.Br(),
            html.H5('Elnakka Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[2]
                ]),
                dbc.Col([
                    ttranks[2]
                ]),
                dbc.Col([
                    hsranks[2]
                ])
            ]),
            html.Br(),
            html.H5('Dalarna Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[3]
                ]),
                dbc.Col([
                    ttranks[3]
                ]),
                dbc.Col([
                    hsranks[3]
                ])
            ]),
            html.Br(),
            html.H5('Rotkamm Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[4]
                ]),
                dbc.Col([
                    ttranks[4]
                ]),
                dbc.Col([
                    hsranks[4]
                ])
            ]),
            html.Br(),
            html.H5('Saint Luvette Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[5]
                ]),
                dbc.Col([
                    ttranks[5]
                ]),
                dbc.Col([
                    hsranks[5]
                ])
            ]),
            html.Br(),
            html.H5('Passo Grolla Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[6]
                ]),
                dbc.Col([
                    ttranks[6]
                ]),
                dbc.Col([
                    hsranks[6]
                ])
            ]),
            html.Br(),
            html.H5('Ben Ailig Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[7]
                ]),
                dbc.Col([
                    ttranks[7]
                ]),
                dbc.Col([
                    hsranks[7]
                ])
            ]),
            html.Br(),
            html.H5('Mount Fairview Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[8]
                ]),
                dbc.Col([
                    ttranks[8]
                ]),
                dbc.Col([
                    hsranks[8]
                ])
            ]),
            html.Br(),
            html.H5('Pinecone Peaks Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    overallranks[9]
                ]),
                dbc.Col([
                    ttranks[9]
                ]),
                dbc.Col([
                    hsranks[9]
                ])
            ]),
        ])
    else:
        return

records_layout = html.Div([
    Header(app),
    dbc.Row([
        sidebar,
        dbc.Col([
            html.Br(),
            html.H3('GMA World Records and Rankings'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.H5('Select Record Type'),
                    dcc.Dropdown(
                        id='recordselect',
                        options=[
                            {'label': 'All', 'value': 'all'},
                            {'label': 'Time Trial', 'value': 'timetrial'},
                            {'label': 'High Score', 'value': 'highscore'},
                            {'label': 'Mountain Pt Ranking', 'value': 'mountain'}
                        ],
                        value='all',
                        searchable=False
                    ),
                ]),
                dbc.Col([
                    html.H5('Sort By'),
                    dcc.Dropdown(
                        id='sortselect',
                        options=[
                            {'label': 'Default (Mountain)', 'value': 'def'},
                            {'label': 'Newest to Oldest', 'value': 'n2o'},
                            {'label': 'Oldest to Newest', 'value': 'o2n'},
                            {'label': 'Challenge Type', 'value': 'chaltype'},
                            {'label': 'Player', 'value': 'player'},
                        ],
                        value='def',
                        searchable=False
                    ),
                ]),
                dbc.Col([
                    html.Div([
                        html.H5(' Community Sum of Best: '+convertMillis(int(totsumofbest))+' ')
                    ],
                    style={'border':'2px black solid','text-align': 'Center'
                        }
                    )
                ])
            ],
            justify='start',
            ),
            html.Br(),
            dbc.Row([
                html.Div(id='record-content')
            ])
        ],
        style={'margin-left':20})
    ],
    style={'padding-left':20})
])
