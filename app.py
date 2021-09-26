
import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import time
from time import strftime
from time import gmtime
from datetime import datetime

import dash  # (version 1.12.0)
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import pathlib
from dash.dependencies import Input, Output
from utils import Header, sidebar

from helpers import calcHSpoints, get_challenge_names, getTDcount, recentWRs, recentPBs, getchallengeImage, sortwrdata, convertMillis, convertMillisNoHours, calcSumofBests
from Mountains import mountain_layout, mountaincontent, graphinfo, challengeinfo
from recordsandrankings import makemountainWRs, makemountainrankings, mountainrankpage, records_layout
from playerpage import makecomparisonPB, makemountainPBs, makePBdf, player_layout, update_player_page, player_compare
from archive import archive_layout

PATH = pathlib.Path(__file__)
DATA_PATH = PATH.joinpath("../data").resolve()

external_stylesheets = [dbc.themes.BOOTSTRAP]
numchallenges = 260

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

server = app.server

df = pd.read_csv(DATA_PATH.joinpath("out.csv"))
hirdf = pd.read_csv(DATA_PATH.joinpath("hirschalm.csv"))
waldf = pd.read_csv(DATA_PATH.joinpath("waldtal.csv"))
elndf = pd.read_csv(DATA_PATH.joinpath("elnakka.csv"))
daldf = pd.read_csv(DATA_PATH.joinpath("dalarna.csv"))
rotdf = pd.read_csv(DATA_PATH.joinpath("rotkamm.csv"))
saidf = pd.read_csv(DATA_PATH.joinpath("saint luvette.csv"))
pasdf = pd.read_csv(DATA_PATH.joinpath("passo grolla.csv"))
bendf = pd.read_csv(DATA_PATH.joinpath("ben ailig.csv"))
moudf = pd.read_csv(DATA_PATH.joinpath("mount fairview.csv"))
pindf = pd.read_csv(DATA_PATH.joinpath("pinecone peaks.csv"))
allwrs = pd.read_csv(DATA_PATH.joinpath("allwrs.csv"))
sortedwrs = pd.read_csv(DATA_PATH.joinpath("sortedwrs.csv"))
challenges = pd.read_csv(DATA_PATH.joinpath("gmachallenges.csv"))
ttwrs = pd.read_csv(DATA_PATH.joinpath("ttwrs.csv"))
allpbs = pd.read_csv(DATA_PATH.joinpath("allpbs.csv"))
overallrankdf = pd.read_csv(DATA_PATH.joinpath("totalrank.csv"))
ttrankdf = pd.read_csv(DATA_PATH.joinpath("totalttrank.csv"))
hsrankdf = pd.read_csv(DATA_PATH.joinpath("totalhsrank.csv"))
achievmentsdf = pd.read_csv(DATA_PATH.joinpath("achievments.csv"))
TDdf = pd.read_csv(DATA_PATH.joinpath("TDDF.csv"))

mountains_list = ['Hirschalm', 'Waldtal', 'Elnakka', 'Dalarna', 'Rotkamm', 'Saint Luvette',
                  'Passo Grolla', 'Ben Ailig', 'Mount Fairview', 'Pinecone Peaks']

sum_of_bests = calcSumofBests()
tenrecent = recentWRs()

#Home page graphs set up
uniqnames = pd.DataFrame(allwrs['Name'].value_counts().reset_index().values, columns=['Name','Num WRs'])
uniqnamesindex = uniqnames.sort_index(axis = 0, ascending=True)
uniqnamesindex = uniqnamesindex.rename(columns={'Name':'Player'})
uniqcolumns = [{"name": i, "id": i,} for i in (uniqnamesindex.columns)]
wrpie = px.pie(uniqnamesindex, values='Num WRs', names='Player',title='WR Pie Chart')
wrpie.update_layout(title_x=0.5)

#Dropdown challenge selection set up
available_rpi = df['Name'].unique()
allist = available_rpi.tolist()
allsorted = sorted(allist, key=str.casefold)
available_rpi = np.array(allsorted)

app.layout = html.Div([
	dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
])

home_layout = html.Div([
    Header(app),
    dbc.Row([
        sidebar,
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.H3('Welcome',
                        style={'text-decoration':'underline'}
                    ),
                    html.Div(
                        "Welcome to the Grand Mountain Adventure Leaderboards, where the world's best GMA players compete to set the fastest times and highest scores."
                    ),
                    html.Br(),
                    html.Div(
                        "Here you can view current world records and personal bests in the community for every track, as well as cool stats and world record history."
                    ),
                    html.Br(),
                    html.Div(
                        "All submissions have been reviewed by our team of moderators and were achieved using legitimate methods without cheats."
                    ),
                    html.Br(),
                    html.Div(
                        "To submit a score, please fill out the following Google Form. Also, join us on the discord server!"
                    ),
                    dcc.Link(
                        "Score Submission Form",
                        href="https://docs.google.com/forms/d/1n3DL3h3NYxhWCBG0NSrtM48uIE3OGvMfL2MVKdBU_kA/edit",
                        className="scorelink"
                    ), html.Br(),
                    dcc.Link(
                        "GMA Discord",
                        href="https://discord.com/invite/SA4F5WN",
                        className="discordlink"
                    )
                ]),
                dbc.Col([
                html.H3('Recent WRs',
                    style={'text-decoration':'underline'}
                ),
                html.Div(tenrecent['Name'].iloc[0]+' set a new WR for '+tenrecent['challenge name'].iloc[0]+' ('+str(tenrecent['score'].iloc[0])+') '+' at '+tenrecent['Timestamp'].iloc[0]),
                html.Div(tenrecent['Name'].iloc[1]+' set a new WR for '+tenrecent['challenge name'].iloc[1]+' ('+str(tenrecent['score'].iloc[1])+') '+' at '+tenrecent['Timestamp'].iloc[1]),
                html.Div(tenrecent['Name'].iloc[2]+' set a new WR for '+tenrecent['challenge name'].iloc[2]+' ('+str(tenrecent['score'].iloc[2])+') '+' at '+tenrecent['Timestamp'].iloc[2]),
                html.Div(tenrecent['Name'].iloc[3]+' set a new WR for '+tenrecent['challenge name'].iloc[3]+' ('+str(tenrecent['score'].iloc[3])+') '+' at '+tenrecent['Timestamp'].iloc[3]),
                html.Div(tenrecent['Name'].iloc[4]+' set a new WR for '+tenrecent['challenge name'].iloc[4]+' ('+str(tenrecent['score'].iloc[4])+') '+' at '+tenrecent['Timestamp'].iloc[4]),
                html.Div(tenrecent['Name'].iloc[5]+' set a new WR for '+tenrecent['challenge name'].iloc[5]+' ('+str(tenrecent['score'].iloc[5])+') '+' at '+tenrecent['Timestamp'].iloc[5]),
                html.Div(tenrecent['Name'].iloc[6]+' set a new WR for '+tenrecent['challenge name'].iloc[6]+' ('+str(tenrecent['score'].iloc[6])+') '+' at '+tenrecent['Timestamp'].iloc[6]),
                html.Div(tenrecent['Name'].iloc[7]+' set a new WR for '+tenrecent['challenge name'].iloc[7]+' ('+str(tenrecent['score'].iloc[7])+') '+' at '+tenrecent['Timestamp'].iloc[7]),
                html.Div(tenrecent['Name'].iloc[8]+' set a new WR for '+tenrecent['challenge name'].iloc[8]+' ('+str(tenrecent['score'].iloc[8])+') '+' at '+tenrecent['Timestamp'].iloc[8]),
                html.Div(tenrecent['Name'].iloc[9]+' set a new WR for '+tenrecent['challenge name'].iloc[9]+' ('+str(tenrecent['score'].iloc[9])+') '+' at '+tenrecent['Timestamp'].iloc[9]),
                ]) #col
            ]),
            html.Br(),
            html.Hr(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        dt.DataTable(data = uniqnamesindex.to_dict('rows'),
                            columns = uniqcolumns,
                            style_cell = {'text-align':'center'}
                        )
                    ),
                ],
                align = 'center'
                ),
                dbc.Col([
                    html.Div(
                        dcc.Graph(figure=wrpie,
                            config={'displayModeBar': False}
                        )
                    )
                ],
                align = 'center')
            ],
            align = 'center'),
            html.Br(),
            html.Br()
        ],
        style = {'padding-top':20}
        )
    ],
    style = {'padding-left':20}
    )
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/hirschalm':
        return hirschalm_layout
    elif pathname == '/waldtal':
        return waldtal_layout
    elif pathname == '/elnakka':
        return elnakka_layout
    elif pathname == '/dalarna':
        return dalarna_layout
    elif pathname == '/rotkamm':
        return rotkamm_layout
    elif pathname == '/saintluvette':
        return saint_luvette_layout
    elif pathname == '/passogrolla':
        return passo_grolla_layout
    elif pathname == '/benailig':
        return ben_ailig_layout
    elif pathname == '/mountfairview':
        return mount_fairview_layout
    elif pathname == '/pineconepeaks':
        return pinecone_peaks_layout
    elif pathname == '/player-search':
        return player_layout
    elif pathname == '/records-and-rankings':
        return records_layout
    elif pathname == '/archive':
        return archive_layout
    else:
        return home_layout

#Im so sorry about how long this function is, I am terrible at using dash
@app.callback(Output('page-select-content', 'children'), [Input('Player-Select', 'value'), Input('playercompbutton','n_clicks')])
def update_player_layout(playername, n_clicks):
    return update_player_page(playername, n_clicks)
            
@app.callback(Output('player-comp-cont', 'children'), [Input('Player-Select', 'value'),Input('Player-Compare-Select', 'value')])
def player_comparison(orgplayer, playertocomp):
    return player_compare(orgplayer, playertocomp)
@app.callback(Output('record-content', 'children'), [Input('recordselect', 'value'),Input('sortselect','value')])
def update_record(chaltypedrop, sorttype):
    if chaltypedrop != 'mountain':
        sortedcopy = sortedwrs.copy()
        returnstring = 'All'
        rankstring = 'Overall'
        rankdata = overallrankdf
        if chaltypedrop == 'timetrial':
            sortedcopy = sortedcopy[sortedcopy['type'] != 'High score']
            returnstring = 'Time Trial'
            rankstring = returnstring
            rankdata = ttrankdf
        elif chaltypedrop == 'highscore':
            sortedcopy = sortedcopy[sortedcopy['type'] == 'High score']
            returnstring = 'High Score'
            rankstring = returnstring
            rankdata = hsrankdf
        
        mtnranks = mountainrankpage(chaltypedrop)
        sortedcopy = sortedcopy.drop(columns=['Link','Was WR','index','Verified?'])
        sortedcopy = sortedcopy.iloc[: , 1:]
        sortedcopy = sortedcopy[['challenge name','score','Name','Timestamp','OS','chaltype','Mountain','type']]
        sortedcopy = sortedcopy.rename(columns={'challenge name':'Challenge Name','score':'Score','Name':'Player','Timestamp':'Date Set'})
        sortedcopy['Duration'] = (pd.to_datetime('now') - pd.to_datetime(sortedcopy['Date Set'])).dt.days
        sortedcopy['Date Set'] = sortedcopy['Date Set'].str[:10]
        
        mountainwrlist = makemountainWRs(sortedcopy, chaltypedrop)
        
        sortedcopy = sortwrdata(sortedcopy, sorttype)
        
        sortuniqnames = pd.DataFrame(sortedcopy['Player'].value_counts().reset_index().values, columns=['Player','Num WRs'])
        sortuniqnamesindex = sortuniqnames.sort_index(axis = 0, ascending=True)
        sortuniqnamesindex['Rank'] = range(1, len(sortuniqnamesindex) + 1)
        sortuniqnamesindex = sortuniqnamesindex[['Rank','Player','Num WRs']]
        sortuniqcolumns = [{"name": i, "id": i,} for i in (sortuniqnamesindex.columns)]
        
        wrdt = dt.DataTable(
            id='wrtable',
            columns=[{'name': i, 'id': i} for i in sortedcopy.columns],
            css=[{'selector': ".show-hide", "rule": "display: none"}],
            data=sortedcopy.to_dict('rows'),
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
            hidden_columns=['chaltype','Mountain','type'],
            page_size=numchallenges
        )
        
        rankdata['Rank'] = rankdata['Rank']+1
        rankdt = dt.DataTable(
            id='displayrankings',
            columns=[{'name': i, 'id': i} for i in rankdata.columns],
            data=rankdata.to_dict('rows'),
            style_cell = {'text-align':'center'}
        )
        if sorttype != 'def':
            return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Br(),
                        html.H3(returnstring+" World Records"),
                        html.Hr(),
                        html.Br(),
                        wrdt,
                        html.Br(),
                        mtnranks
                        ],
                    style={'margin-left':15}
                    ),
                    dbc.Col([
                        html.Br(),
                        html.H5(rankstring+" WR Totals"),
                        dt.DataTable(data = sortuniqnamesindex.to_dict('rows'),
                            columns = sortuniqcolumns,
                            style_cell = {'text-align':'center'}
                        ),
                        html.Br(),
                        html.Br(),
                        html.H5(rankstring+" Point Rankings"),
                        rankdt
                    ], width=3,
                    style={'margin-left':20})
                ])
            ])
        else:
            return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H3(returnstring+" World Records"),
                        html.Br(),
                        html.H4('Hirschalm 🇦🇹', className='title'),
                        html.Hr(),
                        mountainwrlist[0],
                        html.H4('Hirschalm Sum of Best: '+sum_of_bests[0]),
                        html.Br(),
                        html.H4('Waldtal 🇩🇪'),
                        html.Hr(),
                        mountainwrlist[1],
                        html.H4('Waldtal Sum of Best: '+sum_of_bests[1]),
                        html.Br(),
                        html.H4('Elnakka 🇫🇮'),
                        html.Hr(),
                        mountainwrlist[2],
                        html.H4('Elnakka Sum of Best: '+sum_of_bests[2]),
                        html.Br(),
                        html.H4('Dalarna 🇸🇪'),
                        html.Hr(),
                        mountainwrlist[3],
                        html.H4('Dalarna Sum of Best: '+sum_of_bests[3]),
                        html.Br(),
                        html.H4('Rotkamm 🇨🇭'),
                        html.Hr(),
                        mountainwrlist[4],
                        html.H4('Rotkamm Sum of Best: '+sum_of_bests[4]),
                        html.Br(),
                        html.H4('Saint Luvette 🇫🇷'),
                        html.Hr(),
                        mountainwrlist[5],
                        html.H4('Saint Luvette Sum of Best: '+sum_of_bests[5]),
                        html.Br(),
                        html.H4('Passo Grolla 🇮🇹'),
                        html.Hr(),
                        mountainwrlist[6],
                        html.H4('Passo Grolla Sum of Best: '+sum_of_bests[6]),
                        html.Br(),
                        html.H4('Ben Ailig 🏴󠁧󠁢󠁳󠁣󠁴󠁿'),
                        html.Hr(),
                        mountainwrlist[7],
                        html.H4('Ben Ailig Sum of Best: '+sum_of_bests[7]),
                        html.Br(),
                        html.H4('Mount Fairview 🇨🇦'),
                        html.Hr(),
                        mountainwrlist[8],
                        html.H4('Mount Fairview Sum of Best: '+sum_of_bests[8]),
                        html.Br(),
                        html.H4('Pinecone Peaks 🇺🇸'),
                        html.Hr(),
                        mountainwrlist[9],
                        html.H4('Pinecone Peaks Sum of Best: '+sum_of_bests[9]),
                        html.Br(),
                        mtnranks
                        ],
                    style={'margin-left':15}
                    ),
                    dbc.Col([
                        html.Br(),
                        html.Br(),
                        html.H5(rankstring+" WR Totals"),
                        html.Hr(),
                        dt.DataTable(data = sortuniqnamesindex.to_dict('rows'),
                            columns = sortuniqcolumns,
                            style_cell = {'text-align':'center'}
                        ),
                        html.Br(),
                        html.Br(),
                        html.H5(rankstring+" Point Rankings"),
                        html.Hr(),
                        rankdt
                    ], width=3,
                    style={'margin-left':20,'margin-top':10})
                ])
            ])
    else:
        return html.Div([
            mountainrankpage(chaltypedrop)
        ],style={'margin-left':15}
        )
        
#====== MOUNTAIN STUFF ==========================================================

hirschalm_layout = mountain_layout('Hirschalm','Hir','The First Turns')
waldtal_layout = mountain_layout('Waldtal','Wal','The Woodland Slalom')
elnakka_layout = mountain_layout('Elnakka','Eln','The Elements')
dalarna_layout = mountain_layout('Dalarna','Dal','The Dala Horse Trail')
rotkamm_layout = mountain_layout('Rotkamm','Rot','The Village Run')
saint_luvette_layout = mountain_layout('Saint Luvette','Sai','Tour De Moyen')
passo_grolla_layout = mountain_layout('Passo Grolla','Pas','Loggers Groove')
ben_ailig_layout = mountain_layout('Ben Ailig','Ben','The Swindler')
mount_fairview_layout = mountain_layout('Mount Fairview','Mou','Grand Mountain Cup I')
pinecone_peaks_layout = mountain_layout('Pinecone Peaks','Pin','City Woods')

@app.callback(Output('Hirschalm-content', 'children'), [Input('Hir_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_hir_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Hirschalm')
            
@app.callback(Output('Hir challenge info','children'),Input('Hir_dropdown', 'value'))
def update_hir_info(challenge_selected):
    return challengeinfo(challenge_selected, hirdf)
    
@app.callback(Output('Hirschalm-content2', 'children'), [Input('Hir_dropdown','value'),Input('Players','value')])
def update_graph_hir(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, hirdf)
    
    
@app.callback(Output('Waldtal-content', 'children'), [Input('Wal_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_wal_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Waldtal')

@app.callback(Output('Wal challenge info','children'),Input('Wal_dropdown', 'value'))
def update_wal_info(challenge_selected):
    return challengeinfo(challenge_selected, waldf)
    
@app.callback(Output('Waldtal-content2', 'children'), [Input('Wal_dropdown','value'),Input('Players','value')])
def update_graph_wal(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, waldf)
    
    
@app.callback(Output('Elnakka-content', 'children'), [Input('Eln_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_eln_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Elnakka')

@app.callback(Output('Eln challenge info','children'),Input('Eln_dropdown', 'value'))
def update_eln_info(challenge_selected):
    return challengeinfo(challenge_selected, elndf)
    
@app.callback(Output('Elnakka-content2', 'children'), [Input('Eln_dropdown','value'),Input('Players','value')])
def update_graph_eln(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, elndf)
    
    
@app.callback(Output('Dalarna-content', 'children'), [Input('Dal_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_dal_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Dalarna')

@app.callback(Output('Dal challenge info','children'),Input('Dal_dropdown', 'value'))
def update_dal_info(challenge_selected):
    return challengeinfo(challenge_selected, daldf)
    
@app.callback(Output('Dalarna-content2', 'children'), [Input('Dal_dropdown','value'),Input('Players','value')])
def update_graph_dal(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, daldf)
    
    
@app.callback(Output('Rotkamm-content', 'children'), [Input('Rot_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_rot_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Rotkamm')

@app.callback(Output('Rot challenge info','children'),Input('Rot_dropdown', 'value'))
def update_rot_info(challenge_selected):
    return challengeinfo(challenge_selected, rotdf)
    
@app.callback(Output('Rotkamm-content2', 'children'), [Input('Rot_dropdown','value'),Input('Players','value')])
def update_graph_rot(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, rotdf)
    
    
@app.callback(Output('Saint Luvette-content', 'children'), [Input('Sai_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_sai_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Saint Luvette')

@app.callback(Output('Sai challenge info','children'),Input('Sai_dropdown', 'value'))
def update_sai_info(challenge_selected):
    return challengeinfo(challenge_selected, saidf)
    
@app.callback(Output('Saint Luvette-content2', 'children'), [Input('Sai_dropdown','value'),Input('Players','value')])
def update_graph_sai(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, saidf)
    
    
@app.callback(Output('Passo Grolla-content', 'children'), [Input('Pas_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_pas_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Passo Grolla')

@app.callback(Output('Pas challenge info','children'),Input('Pas_dropdown', 'value'))
def update_pas_info(challenge_selected):
    return challengeinfo(challenge_selected, pasdf)
    
@app.callback(Output('Passo Grolla-content2', 'children'), [Input('Pas_dropdown','value'),Input('Players','value')])
def update_graph_pas(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, pasdf)


@app.callback(Output('Ben Ailig-content', 'children'), [Input('Ben_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_ben_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Ben Ailig')

@app.callback(Output('Ben challenge info','children'),Input('Ben_dropdown', 'value'))
def update_ben_info(challenge_selected):
    return challengeinfo(challenge_selected, bendf)
    
@app.callback(Output('Ben Ailig-content2', 'children'), [Input('Ben_dropdown','value'),Input('Players','value')])
def update_graph_ben(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, bendf)


@app.callback(Output('Mount Fairview-content', 'children'), [Input('Mou_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_mou_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Mount Fairview')

@app.callback(Output('Mou challenge info','children'),Input('Mou_dropdown', 'value'))
def update_mou_info(challenge_selected):
    return challengeinfo(challenge_selected, moudf)
    
@app.callback(Output('Mount Fairview-content2', 'children'), [Input('Mou_dropdown','value'),Input('Players','value')])
def update_graph_mou(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, moudf)
    

@app.callback(Output('Pinecone Peaks-content', 'children'), [Input('Pin_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_pin_rows(challenge_selected, range_selected, player_selected):
    return mountaincontent(challenge_selected, range_selected, player_selected, 'Pinecone Peaks')

@app.callback(Output('Pin challenge info','children'),Input('Pin_dropdown', 'value'))
def update_pin_info(challenge_selected):
    return challengeinfo(challenge_selected, pindf)
    
@app.callback(Output('Pinecone Peaks-content2', 'children'), [Input('Pin_dropdown','value'),Input('Players','value')])
def update_graph_pin(challenge_selected, player_selected):
    return graphinfo(challenge_selected, player_selected, pindf)
    
if __name__ == '__main__':
    app.run_server(debug=True)
