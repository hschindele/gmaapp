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
from helpers import recentPBs, calcHSpoints, convertMillisNoHours, getTDcount

PATH = pathlib.Path(__file__)
DATA_PATH = PATH.joinpath("../data").resolve()

df = pd.read_csv(DATA_PATH.joinpath("out.csv"))
overallrankdf = pd.read_csv(DATA_PATH.joinpath("totalrank.csv"))
achievmentsdf = pd.read_csv(DATA_PATH.joinpath("achievments.csv"))
ttrankdf = pd.read_csv(DATA_PATH.joinpath("totalttrank.csv"))
hsrankdf = pd.read_csv(DATA_PATH.joinpath("totalhsrank.csv"))
allwrs = pd.read_csv(DATA_PATH.joinpath("allwrs.csv"))
sortedwrs = pd.read_csv(DATA_PATH.joinpath("sortedwrs.csv"))
challenges = pd.read_csv(DATA_PATH.joinpath("gmachallenges.csv"))
allpbs = pd.read_csv(DATA_PATH.joinpath("allpbs.csv"))

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

available_rpi = df['Name'].unique()
allist = available_rpi.tolist()
allsorted = sorted(allist, key=str.casefold)
available_rpi = np.array(allsorted)

mountains_list = ['Hirschalm', 'Waldtal', 'Elnakka', 'Dalarna', 'Rotkamm', 'Saint Luvette',
                  'Passo Grolla', 'Ben Ailig', 'Mount Fairview', 'Pinecone Peaks']

recentdf = df.copy()
recentdf['Days Since'] = (pd.to_datetime('now') - pd.to_datetime(recentdf['Timestamp'])).dt.days
recentnames = recentdf[recentdf['Days Since'] <= 30].Name.unique()

def makecomparisonPB(pbdf, orgplayer, playertocomp):
    pblist = []
    orgsum = []
    compsum = []
    for mountain in mountains_list:
        mountaintable = pbdf[pbdf['Mountain'] == mountain]
        orgcolumns =  [{"name": i, "id": i,} for i in (mountaintable.columns)]
        mountaindt = dt.DataTable(
            data=mountaintable.to_dict('rows'),
            columns=orgcolumns,
            css=[{'selector': ".show-hide", "rule": "display: none"}],
            style_header={ 'border': '1px solid black' },
            style_cell={'textAlign':'center','border': '1px solid grey'},
            hidden_columns=['Better','Mountain','type','chaltype'],
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{Better} = 1',
                        'column_id': orgplayer
                    },
                    'backgroundColor': '#c0ff00'
                },
                {
                    'if': {
                        'filter_query': '{Better} = 1',
                        'column_id': playertocomp
                    },
                    'backgroundColor': '#d3d3d3'
                },
                {
                    'if': {
                        'filter_query': '{Better} = 0',
                        'column_id': playertocomp
                    },
                    'backgroundColor': '#c0ff00'
                },
                {
                    'if': {
                        'filter_query': '{Better} = 0',
                        'column_id': orgplayer
                    },
                    'backgroundColor': '#d3d3d3'
                },
                {
                    'if': {
                        'filter_query': '{Better} = 2',
                        'column_id': orgplayer
                    },
                    'backgroundColor': '#d3d3d3'
                },
                {
                    'if': {
                        'filter_query': '{Better} = 2',
                        'column_id': playertocomp
                    },
                    'backgroundColor': '#d3d3d3'
                }
            ],
            fill_width=False,
        )
        pblist.append(mountaindt)
        ttdt = mountaintable[mountaintable['type'] == 'Time Trial']
        if 'No Score' in ttdt[orgplayer].values:
            orgsum.append('Incomplete')
        else:
            ttdt[orgplayer] = pd.to_numeric(ttdt[orgplayer])
            presum = (ttdt[orgplayer].sum())*1000
            sumofbest = convertMillisNoHours(int(presum))
            orgsum.append(sumofbest)
        if 'No Score' in ttdt[playertocomp].values:
            compsum.append('Incomplete')
        else:
            ttdt[playertocomp] = pd.to_numeric(ttdt[playertocomp])
            presum = (ttdt[playertocomp].sum())*1000
            sumofbest = convertMillisNoHours(int(presum))
            compsum.append(sumofbest)
    return pblist, orgsum, compsum

def makemountainPBs(pbdf):
    pbtables = []
    sumofbests = []
    for mountain in mountains_list:
        mountaincopy = pbdf[pbdf['Mountain'] == mountain]
        ttdt = mountaincopy[mountaincopy['type'] == 'Time Trial']
        if 'No Score' in ttdt['Time / Score'].values:
            sumofbests.append('Incomplete')
        else:
            ttdt['Time / Score'] = pd.to_numeric(ttdt['Time / Score'])
            presum = (ttdt['Time / Score'].sum())*1000
            sumofbest = convertMillisNoHours(int(presum))
            sumofbests.append(sumofbest)
        playerdt = dt.DataTable(
            data=mountaincopy.to_dict('rows'),
            columns=[{'name': i, 'id': i} for i in mountaincopy.columns],
            css=[{'selector': ".show-hide", "rule": "display: none"}],
            style_header={ 'border': '1px solid black' },
            style_cell={'textAlign':'center','border': '1px solid grey'},
            fill_width=False,
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
            hidden_columns=['type','Mountain','chaltype']
        )
        pbtables.append(playerdt)
    return pbtables, sumofbests

def makePBdf(playername):
        recentpbs = recentPBs(playername)
        ttsubstotal = 0
        hssubstotal = 0
        ttranksum = 0
        hsranksum = 0
        allcopy = df.copy()
        allcopy = allcopy[allcopy['Name'] == playername]
        playerwrs = allwrs[allwrs['Name'] == playername]
        numcurwr = len(playerwrs.index)
        prevplayerwrs = allcopy[allcopy['Was WR'] == True]
        prevwrcount = len(prevplayerwrs.index)
        chaldf = challenges.copy()
        chaldf.reset_index(drop=True)
        chaldf['Time / Score'] = 0
        chaldf['Points'] = 0
        chaldf['Rank'] = 'N/A'
        ind = 0
        #calculate best challenge score for player
        for chalname in chaldf['Challenge Name']:
            chalpbs = allpbs[allpbs['challenge name'] == chalname]
            curcopy = allcopy[allcopy['challenge name'] == chalname]
            chalrows = chaldf[chaldf['Challenge Name'] == chalname]
            if curcopy.empty:
                chaldf['Time / Score'].iloc[ind] = "No Score"
            elif curcopy['type'].iloc[0] == 'High score':
                chalpbs = chalpbs.sort_values('score', ascending=False)
                chalpbs['Rank'] = np.arange(1, chalpbs.shape[0]+1)
                chalscore = curcopy['score'].max()
                chaldf['Time / Score'].iloc[ind] = chalscore
                rankrow = chalpbs[chalpbs['score'] == chalscore]
                rank = rankrow['Rank'].iloc[0]
                hsranksum += rank
                hssubstotal += 1
                chaldf['Rank'].iloc[ind] = rank
                if chalrows['TD'].iloc[0] > 1:
                    wr = float(allwrs[allwrs['challenge name'] == chalname].score.iloc[0])
                    points = int(calcHSpoints(chalrows['TD'].iloc[0], 10000, wr, 20000, chalscore))+1
                    #print('Name: '+curchal+' TD: '+str(curchaldf['TD'])+' WR: '+str(wr)+' score: '+str(score)+' points: '+str(points))
                    if points < 0:
                        points = 0
                else:
                    points = 0
                chaldf['Points'].iloc[ind] = points
            else:
                chalpbs = chalpbs.sort_values('score')
                chalpbs['Rank'] = np.arange(1, chalpbs.shape[0]+1)
                chalscore = curcopy['score'].min()
                chaldf['Time / Score'].iloc[ind] = chalscore
                rankrow = chalpbs[chalpbs['score'] == chalscore]
                rank = rankrow['Rank'].iloc[0]
                ttranksum += rank
                ttsubstotal += 1
                points = 0
                chaldf['Rank'].iloc[ind] = rank
                if chalrows['TD'].iloc[0] > chalscore:
                    points = int(10000*((chalrows['TD'] - chalscore)+1))
                else:
                    points = int(625*(2**((4*(chalrows['DD']) - 3*chalrows['TD'] -chalscore)/(chalrows['DD']-chalrows['TD']))))
                chaldf['Points'].iloc[ind] = points
                
            ind += 1
            
        chaldf[chaldf['Points'] > 10000] = chaldf[chaldf['Points'] > 10000].round({'Points':-2})
        playerdata = chaldf.to_dict('rows')
        playercolumns =  [{"name": i, "id": i,} for i in (chaldf.columns)]
        
        if (ttsubstotal == 0) or (hssubstotal == 0):
            if ttsubstotal == 0:
                avgrank = hsranksum/hssubstotal
                avghs = avgrank
                avgtt = 0
            else:
                avgrank = (ttranksum)/(ttsubstotal)
                avgtt = avgrank
                avghs = 0
        
        else:
            avgrank = (ttranksum+hsranksum)/(ttsubstotal+hssubstotal)
            avgtt = ttranksum/ttsubstotal
            avghs = hsranksum/hssubstotal
            
        avgrank = round(avgrank, 2)
        avgtt = round(avgtt, 2)
        avghs = round(avghs, 2)
        
        playerdt = dt.DataTable(
            data=playerdata,
            columns=playercolumns,
            css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
            style_header={ 'border': '1px solid black' },
            style_cell={'textAlign':'center','border': '1px solid grey'},
            fill_width=False,
        )
        return playerdt, avgrank, avgtt, avghs, numcurwr, prevwrcount, recentpbs, chaldf

player_layout = html.Div([
    Header(app),
    dbc.Row([
        sidebar,
        dbc.Col([
            html.Div([
                html.Br(),
                html.H5('Select Player'),
                dcc.Dropdown(id='Player-Select',
                    options=[
                        {'label': i, 'value': i} for i in available_rpi
                    ],
                    value = '',
                    style = {'width': '60%'}
                ),
                html.Button('Toggle Comparison Mode', id='playercompbutton', n_clicks=0),
                html.Hr(),
            ]),
            html.Br(),
            html.Div(id = 'page-select-content')
        ],
        style = {'padding-left':60}
        )
    ],
    style = {'padding-left':20})
])

def update_player_page(playername, n_clicks):
    if playername != '':
        #Make achievment list
        achievmentlist = []
        playerachievments = achievmentsdf[achievmentsdf['Name'] == playername]
        playerachievments = playerachievments.sort_values('Importance', ascending=True)
        numachievments = len(playerachievments.index)
        if numachievments > 7:
            numachievments = 7
        for i in range(0, numachievments):
            award = playerachievments.Award.iloc[i]
            achievmentlist.append(award)
            
        
        overallrank = str(overallrankdf[overallrankdf['Name'] == playername].Rank.iloc[0] + 1)
        ttrank = "N/A"
        hsrank = "N/A"
        ttrankrow = ttrankdf[ttrankdf['Name'] == playername]
        hsrankrow = hsrankdf[hsrankdf['Name'] == playername]
        if not ttrankrow.empty:
            ttrank = ttrankrow['Rank'].iloc[0] + 1
        if not hsrankrow.empty:
            hsrank = hsrankrow['Rank'].iloc[0] + 1
        playerinfo = makePBdf(playername)
        playerdf = playerinfo[7]
        playersectionedinfo = makemountainPBs(playerdf)
        mountainpbs = playersectionedinfo[0]
        pbsumofbests = playersectionedinfo[1]
        playerdf = playerdf.drop(columns=['chaltype'])
        playercolumns =  [{"name": i, "id": i,} for i in (playerdf.columns)]
        playerdt = dt.DataTable(
            data=playerdf.to_dict('rows'),
            columns=playercolumns,
            css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
            style_header={ 'border': '1px solid black' },
            style_cell={'textAlign':'center','border': '1px solid grey'},
            fill_width=False,
        )
        recentpbs = playerinfo[6]
        
        numrecent = 5
        if len(recentpbs.index) < 5:
            numrecent = len(recentpbs.index)
            
        recent_submission_strings = []
        for i in range(0, numrecent):
            substring =  recentpbs['Timestamp'].iloc[i]+' - '+recentpbs['challenge name'].iloc[i]+' - '+str(recentpbs['score'].iloc[i])
            wrtocompare = sortedwrs[sortedwrs['challenge name'] == recentpbs['challenge name'].iloc[i]].iloc[0]
            originalsub = df[df['challenge name'] == recentpbs['challenge name'].iloc[i]]
            originalsub = originalsub[originalsub['Name'] == playername]
            originalsub = originalsub[originalsub['score'] == recentpbs['score'].iloc[i]]
            if wrtocompare['score'] == recentpbs['score'].iloc[i]:
                substring = substring+' - (WR)'
            elif originalsub['Was WR'].iloc[0] == True:
                substring = substring+' - (Prev WR)'
            recent_submission_strings.append(substring)

            
        
        if n_clicks % 2 == 0:
            return dbc.Col([
                html.H3(playername+"'s Personal Bests"),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H4('Hirschalm 🇦🇹'),
                        html.Hr(),
                        mountainpbs[0],
                        html.H4('Hirschalm Sum of Best: '+pbsumofbests[0]),
                        html.Br(),
                        html.H4('Waldtal 🇩🇪'),
                        mountainpbs[1],
                        html.H4('Waldtal Sum of Best: '+pbsumofbests[1]),
                        html.Br(),
                        html.H4('Elnakka 🇫🇮'),
                        mountainpbs[2],
                        html.H4('Elnakka Sum of Best: '+pbsumofbests[2]),
                        html.Br(),
                        html.H4('Dalarna 🇸🇪'),
                        mountainpbs[3],
                        html.H4('Dalarna Sum of Best: '+pbsumofbests[3]),
                        html.Br(),
                        html.H4('Rotkamm 🇨🇭'),
                        mountainpbs[4],
                        html.H4('Rotkamm Sum of Best: '+pbsumofbests[4]),
                        html.Br(),
                        html.H4('Saint Luvette 🇫🇷'),
                        mountainpbs[5],
                        html.H4('Saint Luvette Sum of Best: '+pbsumofbests[5]),
                        html.Br(),
                        html.H4('Passo Grolla 🇮🇹'),
                        mountainpbs[6],
                        html.H4('Passo Grolla Sum of Best: '+pbsumofbests[6]),
                        html.Br(),
                        html.H4('Ben Ailig 🏴󠁧󠁢󠁳󠁣󠁴󠁿'),
                        mountainpbs[7],
                        html.H4('Ben Ailig Sum of Best: '+pbsumofbests[7]),
                        html.Br(),
                        html.H4('Mount Fairview 🇨🇦'),
                        mountainpbs[8],
                        html.H4('Mount Fairview Sum of Best: '+pbsumofbests[8]),
                        html.Br(),
                        html.H4('Pinecone Peaks 🇺🇸'),
                        mountainpbs[9],
                        html.H4('Pinecone Peaks Sum of Best: '+pbsumofbests[9]),
                        html.Br(),
                    ]),
                    dbc.Col([
                        html.Div([
                            html.H3(playername+"'s Info TDs: "+str(getTDcount(playername))+" / 171",
                                style={'text-align': 'Center'}
                            ),
                            html.Hr(),
                            html.Div([
                                html.H5("Rank: "+overallrank,
                                style={'display':'inline-block','margin-left':'30px','margin-right':'30px'}
                                ),
                                html.H5("TT Rank: "+str(ttrank),
                                style={'display':'inline-block','margin-right':'30px'}
                                ),
                                html.H5("HS Rank: "+str(hsrank),
                                style={'display':'inline-block','margin-right':'30px'}
                                )
                                ],
                                style={'text-align': 'Center'}
                            ),
                            html.Hr(),
                            html.Div([
                                html.H5("Avg TT Rank: "+str(playerinfo[2]),
                                style={'display':'inline-block','margin-left':'30px','margin-right':'30px'}
                                ),
                                html.H5("Avg HS Rank: "+str(playerinfo[3]),
                                style={'display':'inline-block','margin-right':'30px'}
                                ),
                                html.H5("Avg Overall Rank: "+str(playerinfo[1]),
                                style={'display':'inline-block','margin-right':'30px'}
                                )
                                ],
                                style={'text-align': 'Center'}
                            ),
                            html.Hr(),
                            html.Div([
                                html.H5("Current WRs: "+str(playerinfo[4]),
                                    style={'display':'inline-block','margin-left':'10','margin-right':'30'}
                                    ),
                                html.H5("Lifetime WRs: "+str(playerinfo[5]),
                                    style={'display':'inline-block','margin-right':'10','margin-left':30}
                                    )
                            ],
                            style={'text-align': 'Center'})
                        ], style={'margin-left':30,'margin-right':30,"border":"2px black solid"}),
                        html.Br(),
                        html.Div([
                            html.H5("Recent Submissions"),
                            html.Hr(),
                            html.Div([html.P(substring) for substring in recent_submission_strings])
                        ],
                        style = {'padding-left':40}),
                        html.Br(),
                        html.Div([
                            html.H5('Achievements'),
                            html.Hr(),
                            html.Div(children=[html.P(award) for award in achievmentlist])
                        ],style = {'padding-left':40})
                    ],
                    style = {'padding-left':50})
                ])
            ],
            align='center')
        else:
            return html.Div([
                html.H5("Compare "+playername+" with another player"),
                dcc.Dropdown(id='Player-Compare-Select',
                        options=[
                            {'label': i, 'value': i} for i in available_rpi
                        ],
                        value = '',
                        style = {"width": "60%"}
                ),
                html.Br(),
                html.Div(id = 'player-comp-cont')
            ])
    else:
        disprank = 1
        ranklist = []
        for name in overallrankdf.Name:
            ranklist.append(str(disprank)+'. '+name)
            disprank += 1
        return dbc.Row([
                dbc.Col([
                    html.H5('Players by name'),
                    html.Hr(),
                    html.Div(children=[html.P(name) for name in available_rpi],
                             style = {'maxHeight': '500px','overflow': 'scroll'}
                            )
                ]),
                dbc.Col([
                    html.H5('Players by rating'),
                    html.Hr(),
                    html.Div(children=[html.P(name) for name in ranklist],
                             style = {'maxHeight': '500px','overflow': 'scroll'}
                    )
                ]),
                dbc.Col([
                    html.H5('Active this month'),
                    html.Hr(),
                    html.Div(children=[html.P(name) for name in recentnames],
                             style = {'maxHeight': '500px','overflow': 'scroll'}
                    )
                ])
            ])

def player_compare(orgplayer, playertocomp):
    playerinfo = makePBdf(orgplayer)
    playerdf = playerinfo[7]
    playerdf = playerdf.rename(columns={'Time / Score':orgplayer})
    playerdf = playerdf.drop(columns=['DD','TD','Points','Rank'])
    if playertocomp != '':
        compinfo = makePBdf(playertocomp)
        compdf = compinfo[7]
        compdf = compdf.rename(columns={'Time / Score':playertocomp})
        compdf = compdf.drop(columns=['DD','TD','Points'])
        playerdf[playertocomp] = compdf[playertocomp]
        playerdf['Better'] = 0
        ind = 0
        while ind < len(playerdf.index):
            if (playerdf[orgplayer].iloc[ind] == 'No Score') and (playerdf[playertocomp].iloc[ind] == 'No Score'):
                playerdf['Better'].iloc[ind] = 2
            elif playerdf[orgplayer].iloc[ind] == 'No Score':
                playerdf['Better'].iloc[ind] = 0
            elif playerdf[playertocomp].iloc[ind] == 'No Score':
                playerdf['Better'].iloc[ind] = 1
            elif playerdf['type'].iloc[ind] == 'Time Trial':
                if playerdf[orgplayer].iloc[ind] < playerdf[playertocomp].iloc[ind]:
                    playerdf['Better'].iloc[ind] = 1
                elif playerdf[orgplayer].iloc[ind] > playerdf[playertocomp].iloc[ind]:
                    playerdf['Better'].iloc[ind] = 0
                else:
                    playerdf['Better'].iloc[ind] = 2
            else:
                if playerdf[orgplayer].iloc[ind] > playerdf[playertocomp].iloc[ind]:
                    playerdf['Better'].iloc[ind] = 1
                elif playerdf[orgplayer].iloc[ind] < playerdf[playertocomp].iloc[ind]:
                    playerdf['Better'].iloc[ind] = 0
                else:
                    playerdf['Better'].iloc[ind] = 2
            ind += 1
        tts = playerdf[playerdf['type'] == 'Time Trial']
        hs = playerdf[playerdf['type'] == 'High Score']
        orgtt = len(tts[tts['Better'] == 1])
        comptt = len(tts[tts['Better'] == 0])
        drawtt = len(tts[tts['Better'] == 2])
        orghs = len(hs[hs['Better'] == 1])
        comphs = len(hs[hs['Better'] == 0])
        drawhs = len(hs[hs['Better'] == 2])
        compinfo = makecomparisonPB(playerdf, orgplayer, playertocomp)
        pblist = compinfo[0]
        orgsum = compinfo[1]
        compsum = compinfo[2]
        return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H3("Comparing against "+str(playertocomp)),
                        html.Hr(),
                        html.H4('Hirschalm 🇦🇹'),
                        pblist[0],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[0]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[0]),
                        html.Br(),
                        html.H4('Waldtal 🇩🇪'),
                        pblist[1],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[1]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[1]),
                        html.Br(),
                        html.H4('Elnakka 🇫🇮'),
                        pblist[2],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[2]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[2]),
                        html.Br(),
                        html.H4('Dalarna 🇸🇪'),
                        pblist[3],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[3]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[3]),
                        html.Br(),
                        html.H4('Rotkamm 🇨🇭'),
                        pblist[4],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[4]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[4]),
                        html.Br(),
                        html.H4('Saint Luvette 🇫🇷'),
                        pblist[5],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[5]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[5]),
                        html.Br(),
                        html.H4('Passo Grolla 🇮🇹'),
                        pblist[6],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[6]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[6]),
                        html.Br(),
                        html.H4('Ben Ailig 🏴󠁧󠁢󠁳󠁣󠁴󠁿'),
                        pblist[7],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[7]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[7]),
                        html.Br(),
                        html.H4('Mount Fairview 🇨🇦'),
                        pblist[8],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[8]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[8]),
                        html.Br(),
                        html.H4('Pinecone Peaks 🇺🇸'),
                        pblist[9],
                        html.H5(orgplayer+' Sum of Bests: '+orgsum[9]),
                        html.H5(playertocomp+' Sum of Bests: '+compsum[9]),
                        html.Br(),
                    ],
                    style={'margin-top':26}),
                    dbc.Col([
                        html.Div([
                            html.Br(),
                            html.H3(orgplayer+" VS "+playertocomp,style={'textAlign':'center'}),
                            html.Hr(),
                            dbc.Row([
                                dbc.Col([
                                    html.H4('TT Comparison',style={'textAlign':'center'}),
                                    html.H6(orgplayer+": "+str(orgtt)+" - "+playertocomp+": "+str(comptt),style={'textAlign':'center'}),
                                    html.H6("("+str(drawtt)+" draws)",style={'textAlign':'center'})
                                ]),
                                dbc.Col([
                                    html.H4('HS Comparison',style={'textAlign':'center'}),
                                    html.H6(orgplayer+": "+str(orghs)+" - "+playertocomp+": "+str(comphs),style={'textAlign':'center'}),
                                    html.H6("("+str(drawhs)+" draws)",style={'textAlign':'center'})
                                ])
                            ]),
                            html.Hr(),
                            dbc.Col([
                                html.H4('Overall Comparison',style={'textAlign':'center'}),
                                html.H5(orgplayer+": "+str(orghs+orgtt)+" - "+playertocomp+": "+str(comphs+comptt)+" - ("+str(drawhs+drawtt)+" draws)",style={'textAlign':'center'})
                            ])
                        ],
                        style={'margin-right':20,"border":"2px black solid"}
                        )
                    ])
                ])
            ])
    else:
        return
