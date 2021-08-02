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

available_rpi = df['Name'].unique()
allist = available_rpi.tolist()
allsorted = sorted(allist, key=str.casefold)
available_rpi = np.array(allsorted)

def mountain_layout(mountain, prefix, defchal):
    return html.Div(
        [
            Header(app),
            dbc.Row([
                sidebar,
                html.Br(),
                dbc.Col([
                    dbc.Row([dbc.Col([
                    html.H3("Select Challenge",
                        className = "subtitle",
                        style={'margin-top':'40px','margin-left':'20px','text-decoration':'underline'}
                    ),
                        dcc.Dropdown(id=prefix+'_dropdown',
                            options=[{'label': i, 'value': i} for i in get_challenge_names(mountain)['Challenge Name']],
                            value = defchal,
                            style = {"width": "60%",'margin-left':'10px'},
                        ),
                        dcc.Dropdown(id='Range',
                            options=[
                                {'label': 'Top 5', 'value': 'Top 5'},
                                {'label': 'Top 10', 'value': 'Top 10'},
                                {'label': 'All', 'value': 'All'}
                            ],
                            value = 'Top 5',
                            style = {"width": "40%",'margin-left':'10px'},
                        )]),
                        dbc.Col([html.Div(id=prefix+' challenge info',style={"border":"2px black solid"}) ], style={'padding-right':30,'padding-top':50})
                    ]),
                    html.Br(),
                    html.Div(id=mountain+'-content'),
                    html.Br(),
                    html.H5('Select players to compare',
                        style={'padding-left':70,'text-decoration':'underline'}
                    ),
                    html.Div([
                        dcc.Dropdown(id='Players',
                        options=[{'label': i, 'value': i} for i in available_rpi],
                        value='',
                        style = {"width": "50%"},
                        multi=True
                        )],
                        style = {'padding-left':70}
                    ),
                    html.Div(id=mountain+'-content2')
                ])
            ],
            style = {'padding-left':20})
        ],
)

def mountaincontent(challenge_selected, range_selected, player_selected, mountain):
    istt = True
    type = 'Time'
    wrdff = allwrs.copy()
    if challenges[challenges['Challenge Name'] == challenge_selected].iloc[0].type != 'Time Trial':
        istt = False
        type = 'Score'
        
    dff = allpbs.copy()
    dff = dff[dff["challenge name"] == challenge_selected]
    num = 5
    
    if range_selected == "Top 10":
        num = 10
    elif range_selected == "All":
        num = dff['Name'].nunique()
        
    sumdt = ttwrs[ttwrs['Mountain'] == mountain]
    sumofbest = (sumdt['score'].sum())*1000
    wrdff = wrdff[wrdff['Mountain'] == mountain]
    wrdff = wrdff[['challenge name', 'score','Name','Timestamp','OS','chaltype']]
    
    if num > dff['Name'].nunique():
        num = dff['Name'].nunique()
        
    if istt:
        dff10 = dff.sort_values(by=['score'])
        dff10 = dff10.nsmallest(int(num), 'score')
    else:
        dff10 = dff.sort_values(by=['score'], ascending=False)
        dff10 = dff10.nlargest(int(num), 'score')
        
    dff10['Rank'] = np.arange(1, dff10.shape[0]+1)
        
    dff10 = dff10[['Rank', 'score','Name','Timestamp','OS']]
    dff10 = dff10.rename(columns={'Timestamp':'Date Set', 'score':'Score'})
    wrdff = wrdff.rename(columns={'Timestamp':'Date Set', 'challenge name':'Challenge Name', 'score':'Score'})
    wrdff = wrdff.set_index('Challenge Name')
    wrdff = wrdff.reindex(index=get_challenge_names(mountain)['Challenge Name'])
    wrdff = wrdff.reset_index()
        
    columns =  [{"name": i, "id": i,} for i in (dff10.columns)]
    wrdata = wrdff.to_dict('rows')
    wrcolumns =  [{"name": i, "id": i,} for i in (wrdff.columns)]
    
    curchaldt = dt.DataTable(
        data=dff10.to_dict('rows'),
        columns=columns,
        css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
        style_header={ 'border': '1px solid black' },
        style_cell={'textAlign':'center','border': '1px solid grey'},
        fill_width=False,
        style_cell_conditional=[
        {'if': {'column_id': 'Date Set'},
         'width': '200px'},
        {'if': {'column_id': 'Rank'},
         'width': '60px'},
        {'if': {'column_id': 'OS'},
         'width': '90px'},
        {'if': {'column_id': 'Score'},
         'width': '60px'},
        {'if': {'column_id': 'Name'},
         'width': '200px','textAlign':'left'},
        ]
    )
    
    curwrsdt = dt.DataTable(
        data=wrdata,
        columns = wrcolumns,
        css=[{'selector': ".show-hide", "rule": "display: none"}],
        style_header={ 'border': '1px solid black' },
        style_cell={'textAlign':'center','border': '1px solid grey'},
        fill_width=False,
                style_cell_conditional=[
        {'if': {'column_id': 'Date Set'},
         'width': '200px'},
        {'if': {'column_id': 'OS'},
         'width': '90px'},
        {'if': {'column_id': 'Score'},
         'width': '60px'},
        {'if': {'column_id': 'Name'},
         'width': '200px', 'textAlign':'left'},
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
        hidden_columns=['chaltype']
    )
    
    return dbc.Row([dbc.Col([
            html.H2(challenge_selected+" Top Scores",
                style={'text-decoration':'underline','padding-left':20}
            ),
                html.Div([curchaldt], style={'display': 'inline-block','padding-left':20}
                )
            ]),
            dbc.Col([
                html.H2(mountain+" WRs",
                    style={'text-decoration':'underline'}
                ),
                html.Div([curwrsdt],
                    style={'display': 'inline-block','padding-right':20}
                ),
                html.H5(mountain+" Sum Of Best: "+convertMillisNoHours(int(sumofbest)),
                    style={'textAlign':'center'}
                )
            ])
        ]
    ),html.Br()
    
def graphinfo(challenge_selected, player_selected, indf):
    istt = True
    type = 'Time'
    wrdff = allwrs.copy()
    if challenges[challenges['Challenge Name'] == challenge_selected].iloc[0].type != 'Time Trial':
        istt = False
        type = 'Score'
    dff = indf.copy()
    dff = dff[dff["challenge name"] == challenge_selected]
    dffpast = dff[dff['Was WR'] == True]
    curnumWRs = dff.shape[0]
    dffpast = dffpast.sort_values(by=['Timestamp'])
    fig = px.line(dffpast, x='Timestamp', y='score',
        labels={
            'Timestamp': 'Date Set',
            'score': type
        },
        title=challenge_selected+" World Record History")
    
    fig.update_traces(mode="markers+lines",hovertemplate = dffpast['Name']+'<br>'+'%{y}'+'<br>'+dffpast['OS']+'<br>'+dffpast['Timestamp'])
    fig.update_layout(hovermode="x", xaxis_tickformat = '%B<br>%Y')
    
    for plname in player_selected:
        if plname != '':
            playerdf = dff[dff['Name']==plname]
            playerdf = playerdf.sort_values(by='Timestamp',ascending=False)
            fig.add_trace(go.Scatter(x=playerdf['Timestamp'],y=playerdf['score'], name=plname,
                hovertemplate = playerdf['Name']+'<br>'+'%{y}'+'<br>'+playerdf['OS']+'<br>'+playerdf['Timestamp']))
                
    fig.update_xaxes(dtick="M1")
                
    return dcc.Graph(figure=fig,
    config={
        'displayModeBar': False
    })

def challengeinfo(challenge_selected, indf):
    istt = True
    type = 'Time'
    if challenges[challenges['Challenge Name'] == challenge_selected].iloc[0].type != 'Time Trial':
        istt = False
        type = 'Score'
    dff = indf.copy()
    dff = dff[dff["challenge name"] == challenge_selected]
    dffpast = dff[dff['Was WR'] == True]
    curnumWRs = dffpast.shape[0]
    curchal = challenges[challenges['Challenge Name'] == challenge_selected]
    td = curchal['TD'].iloc[0]
    dd = curchal['DD'].iloc[0]
    wr = sortedwrs[sortedwrs['challenge name'] == challenge_selected].iloc[0]
    wrstring = str(wr['score'])
    size = len(wrstring)
    if (not istt) and (size > 5):
        wrstring = wrstring[:size - 2]
    chaltype = curchal.chaltype.iloc[0]
    
    return [html.Div([
                html.Div(
                    getchallengeImage(chaltype, '60%', '60%'), style={'display':'inline-block','margin-right':'4px'}
                ),
                html.Div(
                    html.H3(challenge_selected+" Info "), style={'display':'inline-block'}
                ),
                html.Div(
                    getchallengeImage(chaltype, '60%', '60%'), style={'display':'inline-block','margin-left':'8px'}
                )
            ], style={'textAlign':'center'}),
            html.Div([
                html.H5("DD: "+str(dd),
                style={'display':'inline-block','margin-left':'30px','margin-right':'30px'}
                ),
                html.H5("TD: "+str(td),
                style={'display':'inline-block','margin-right':'30px'}
                ),
                html.H5("WR: "+wrstring,
                style={'display':'inline-block','margin-right':'30px'}
                ),
                html.H5("Total Wrs Set: "+str(curnumWRs),
                style={'display':'inline-block','margin-right':'30px'}
                )
            ],
                style={'text-align': 'Center'}
            ),
            html.H5("Current WR Holder: "+wr['Name'],
            style={'text-align': 'Center'}
            )]
