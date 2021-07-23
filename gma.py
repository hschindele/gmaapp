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
from utils import Header

external_stylesheets = [dbc.themes.BOOTSTRAP]
numchallenges = 260

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

df = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/out.csv")
hirdf = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/hirschalm.csv")
waldf = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/waldtal.csv")
allwrs = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/allwrs.csv")
sortedwrs = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/sortedwrs.csv")
challenges = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/gmachallenges.csv")
ttwrs = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/ttwrs.csv")
allpbs = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/allpbs.csv")
overallrankdf = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/totalrank.csv")
ttrankdf = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/totalttrank.csv")
hsrankdf = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/totalhsrank.csv")
achievmentsdf = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/achievments.csv")
TDdf = pd.read_csv("/Users/hschindele/Desktop/gmaapp/data/TDDF.csv")

mountains_list = ['Hirschalm', 'Waldtal', 'Elnakka', 'Dalarna', 'Rotkamm', 'Saint Luvette',
                  'Passo Grolla', 'Ben Ailig', 'Mount Fairview', 'Pinecone Peaks']

recentdf = df.copy()
recentdf['Days Since'] = (pd.to_datetime('now') - pd.to_datetime(recentdf['Timestamp'])).dt.days
recentnames = recentdf[recentdf['Days Since'] <= 30].Name.unique()

def getTDcount(player):
    return int(TDdf[TDdf['Name'] == player].TD.iloc[0])

def calcSumofBests():
    sum_of_bests = []
    sumdt = sortedwrs[sortedwrs['type'] != 'High score']
    for mountain in mountains_list:
        mtnsumdt = sumdt[sumdt['Mountain'] == mountain]
        sumofbest = (mtnsumdt['score'].sum())*1000
        sum_of_bests.append(sumofbest)
    return sum_of_bests

sum_of_bests = calcSumofBests()
                  
def calcHSpoints(x1,y1,x2,y2,score):
    gradient = (np.log(y2)-np.log(y1))/(x2-x1)
    intercept = np.log(y1)-(gradient*x1)
    return np.exp(intercept)*((np.exp(gradient))**score)

def sortwrdata(data, sorttype):
    if sorttype == 'n2o':
        data = data.sort_values('Date Set', ascending=False).reset_index(drop=True)
    elif sorttype == 'o2n':
        data = data.sort_values('Date Set', ascending=True).reset_index(drop=True)
    elif sorttype == 'chaltype':
        count_df = pd.DataFrame(data.chaltype.value_counts())
        new_index = count_df.merge(data[['chaltype']], left_index=True, right_on='chaltype')
        data = data.reindex(new_index.index)
    elif sorttype == 'player':
        count_df = pd.DataFrame(data.Player.value_counts())
        new_index = count_df.merge(data[['Player']], left_index=True, right_on='Player')
        data = data.reindex(new_index.index)
    return data

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

totsumofbest = (sortedwrs[sortedwrs['type'] != 'High score'].score.sum())*1000

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
                        dbc.Col([html.Div(id='challenge info',style={"border":"2px black solid"}) ], style={'padding-right':30,'padding-top':50})
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

def get_challenge_names(mountain):
    mtddf = challenges[challenges['Mountain'] == mountain]
    return mtddf

def convertMillis(millis):
    mils = abs(millis) % 1000
    seconds=int((millis/1000)%60)
    minutes=int((millis/(1000*60))%60)
    hours=int((millis/(1000*60*60))%60)
    if minutes < 10:
        minutes = '0'+str(minutes)
    if seconds < 10:
        seconds = '0'+str(seconds)
    if mils < 10:
        seconds = '0'+str(mils)
    return str(hours)+":"+str(minutes)+":"+str(seconds)+"."+str(mils)[:2]

def convertMillisNoHours(millis):
    mils = abs(millis) % 1000
    seconds=int((millis/1000)%60)
    minutes=int((millis/(1000*60))%60)
    if seconds < 10:
        seconds = '0'+str(seconds)
    if mils < 10:
        seconds = '0'+str(mils)
    return str(minutes)+":"+str(seconds)+"."+str(mils)[:2]


def recentWRs():
    wrdf = allwrs.copy()
    wrdf = wrdf.sort_values(by=['Timestamp'], ascending=False)
    return wrdf.head(10)

def recentPBs(playername):
    pbdf = allpbs[allpbs['Name'] == playername]
    pbdf = pbdf.sort_values(by=['Timestamp'], ascending=False)
    return pbdf.head(5)

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
        del chaldf['Mountain']
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

tenrecent = recentWRs()

SIDEBAR_STYLE = {
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "10rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
CONTENT_STYLE = {
    
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H5("Page Select"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", active="exact"),
                dbc.NavLink("Player Search", href="/player-search", active="exact"),
                dbc.NavLink("Records and Rankings", href="/records-and-rankings", active="exact")
            ],
            vertical=True,
            pills=True
        ),
        html.Hr(),
        html.H5("Mountain Pages"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Hirschalm", href="/hirschalm", active="exact"),
                dbc.NavLink("Waldtal", href="/waldtal", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

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
            ],
            style = {'margin-right':'200px'}),
            html.Br(),
            dbc.Row([
                html.Div(id = 'page-select-content')
            ])
        ],
        style = {'padding-left':60}
        )
    ],
    style = {'padding-left':20})
])

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
                            {'label': 'By Mountain', 'value': 'mountain'}
                        ],
                        value='all',
                        searchable=False,
                        style={
                            'width':'70%'
                        }
                    ),
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
                        searchable=False,
                        style={
                            'width':'70%'
                        }
                    ),
                ],width=3
                ),
                html.Div([
                    html.H5(' Community Sum of Best: '+convertMillis(int(totsumofbest))+' ')
                ],
                style={'border':'2px black solid','text-align': 'Center','verticalAlign':'middle'
                    }
                )
            ]),
            html.Br(),
            dbc.Row([
                html.Div(id='record-content')
            ])
        ],
        style={'margin-left':20})
    ],
    style={'padding-left':20})
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/hirschalm':
        return hirschalm_layout
    elif pathname == '/waldtal':
        return waldtal_layout
    elif pathname == '/player-search':
        return player_layout
    elif pathname == '/records-and-rankings':
        return records_layout
    else:
        return home_layout

#Im so sorry about how long this function is, I am terrible at using dash
@app.callback(Output('page-select-content', 'children'), [Input('Player-Select', 'value'), Input('playercompbutton','n_clicks')])
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
        playerdf = playerdf.drop(columns=['type','chaltype'])
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
        iswrstrings = ['','','','','']
        for ind in range(5):
            wrtocompare = sortedwrs[sortedwrs['challenge name'] == recentpbs['challenge name'].iloc[ind]].iloc[0]
            originalsub = df[df['challenge name'] == recentpbs['challenge name'].iloc[ind]]
            originalsub = originalsub[originalsub['Name'] == playername]
            originalsub = originalsub[originalsub['score'] == recentpbs['score'].iloc[ind]]
            if originalsub['Was WR'].iloc[0] == True:
                iswrstrings[ind] = ' - (Prev WR)'
            if wrtocompare['score'] == recentpbs['score'].iloc[ind]:
                iswrstrings[ind] = ' - (WR)'
        
        if n_clicks % 2 == 0:
            return dbc.Col([
                html.H5(playername+"'s Personal Bests",
                ),
                dbc.Row([
                    playerdt,
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
                            html.Div(recentpbs['Timestamp'].iloc[0]+' - '+recentpbs['challenge name'].iloc[0]+' - '+str(recentpbs['score'].iloc[0])+iswrstrings[0]),
                            html.Div(recentpbs['Timestamp'].iloc[1]+' - '+recentpbs['challenge name'].iloc[1]+' - '+str(recentpbs['score'].iloc[1])+iswrstrings[1]),
                            html.Div(recentpbs['Timestamp'].iloc[2]+' - '+recentpbs['challenge name'].iloc[2]+' - '+str(recentpbs['score'].iloc[2])+iswrstrings[2]),
                            html.Div(recentpbs['Timestamp'].iloc[3]+' - '+recentpbs['challenge name'].iloc[3]+' - '+str(recentpbs['score'].iloc[3])+iswrstrings[3]),
                            html.Div(recentpbs['Timestamp'].iloc[4]+' - '+recentpbs['challenge name'].iloc[4]+' - '+str(recentpbs['score'].iloc[4])+iswrstrings[4]),
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
            ],
            justify = 'center',
        )
@app.callback(Output('player-comp-cont', 'children'), [Input('Player-Select', 'value'),Input('Player-Compare-Select', 'value')])
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
        playerdf = playerdf.drop(columns=['type','chaltype'])
        orgcolumns =  [{"name": i, "id": i,} for i in (playerdf.columns)]
        orgdt = dt.DataTable(
            data=playerdf.to_dict('rows'),
            columns=orgcolumns,
            css=[{'selector': ".show-hide", "rule": "display: none"}],
            style_header={ 'border': '1px solid black' },
            style_cell={'textAlign':'center','border': '1px solid grey'},
            hidden_columns=['Better'],
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
        return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H3("Comparing against "+str(playertocomp)),
                        html.Hr(),
                        orgdt
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
                                    html.H6(orgplayer+": "+str(orgtt)+" - "+playertocomp+": "+str(comptt)+" - ("+str(drawtt)+" draws)",style={'textAlign':'center'})
                                ]),
                                dbc.Col([
                                    html.H4('HS Comparison',style={'textAlign':'center'}),
                                    html.H6(orgplayer+": "+str(orghs)+" - "+playertocomp+": "+str(comphs)+" - ("+str(drawhs)+" draws)",style={'textAlign':'center'})
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
                        html.H5(returnstring+" World Records"),
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
                        html.H4(returnstring+" World Records"),
                        html.H5('Hirschalm'),
                        mountainwrlist[0],
                        html.H5('Hirschalm Sum of Best: '+convertMillisNoHours(int(sum_of_bests[0]))),
                        html.Br(),
                        html.H5('Waldtal'),
                        mountainwrlist[1],
                        html.H5('Waldtal Sum of Best: '+convertMillisNoHours(int(sum_of_bests[1]))),
                        html.Br(),
                        html.H5('Elnakka'),
                        mountainwrlist[2],
                        html.H5('Elnakka Sum of Best: '+convertMillisNoHours(int(sum_of_bests[2]))),
                        html.Br(),
                        html.H5('Dalarna'),
                        mountainwrlist[3],
                        html.H5('Dalarna Sum of Best: '+convertMillisNoHours(int(sum_of_bests[3]))),
                        html.Br(),
                        html.H5('Rotkamm'),
                        mountainwrlist[4],
                        html.H5('Rotkamm Sum of Best: '+convertMillisNoHours(int(sum_of_bests[4]))),
                        html.Br(),
                        html.H6('Saint Luvette'),
                        mountainwrlist[5],
                        html.H5('Saint Luvette Sum of Best: '+convertMillisNoHours(int(sum_of_bests[5]))),
                        html.Br(),
                        html.H6('Passo Grolla'),
                        mountainwrlist[6],
                        html.H5('Passo Grolla Sum of Best: '+convertMillisNoHours(int(sum_of_bests[6]))),
                        html.Br(),
                        html.H6('Ben Ailig'),
                        mountainwrlist[7],
                        html.H5('Ben Ailig Sum of Best: '+convertMillisNoHours(int(sum_of_bests[7]))),
                        html.Br(),
                        html.H6('Mount Fairview'),
                        mountainwrlist[8],
                        html.H5('Mount Fairview Sum of Best: '+convertMillisNoHours(int(sum_of_bests[8]))),
                        html.Br(),
                        html.H6('Passo Grolla'),
                        mountainwrlist[9],
                        html.H5('Pinecone Peaks Sum of Best: '+convertMillisNoHours(int(sum_of_bests[9]))),
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
                    style={'margin-left':20,'margin-top':10})
                ])
            ])
    else:
        return html.Div([
            mountainrankpage(chaltypedrop)
        ],style={'margin-left':15}
        )
        
#======  HIRSCHALM  ==========================================================

hirschalm_layout = mountain_layout('Hirschalm','Hir','The First Turns')
waldtal_layout = mountain_layout('Waldtal','Wal','The Woodland Slalom')
        
@app.callback(Output('Hirschalm-content', 'children'), [Input('Hir_dropdown', 'value'), Input('Range', 'value'),Input('Players','value')])
def update_rows(challenge_selected, range_selected, player_selected):
    istt = True
    type = 'Time'
    wrdff = allwrs.copy()
    if (challenge_selected == 'Glacier Park') | (challenge_selected == 'The Glacier Kicker'):
        istt = False
        type = 'Score'
        
    dff = allpbs.copy()
    dff = dff[dff["challenge name"] == challenge_selected]
    num = 5
    
    if range_selected == "Top 10":
        num = 10
    elif range_selected == "All":
        num = dff['Name'].nunique()
        
    sumdt = ttwrs[ttwrs['Mountain'] == 'Hirschalm']
    sumofbest = (sumdt['score'].sum())*1000
    wrdff = wrdff[wrdff['Mountain'] == 'Hirschalm']
    wrdff = wrdff[['challenge name', 'score','Name','Timestamp','OS']]
    
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
    wrdff = wrdff.reindex(index=get_challenge_names('Hirschalm')['Challenge Name'])
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
        ]
    )
    
    return dbc.Row([dbc.Col([
            html.H2(challenge_selected+" Top Scores",
                style={'text-decoration':'underline','padding-left':20}
            ),
                html.Div([curchaldt], style={'display': 'inline-block','padding-left':20}
                )
            ]),
            dbc.Col([
                html.H2("Hirschalm WRs",
                    style={'text-decoration':'underline'}
                ),
                html.Div([curwrsdt],
                    style={'display': 'inline-block','padding-right':20}
                ),
                html.H5("Hirschalm Sum Of Best: "+convertMillisNoHours(int(sumofbest)),
                    style={'textAlign':'center'}
                )
            ])
        ]
    ),html.Br()

@app.callback(Output('Hirschalm-content2', 'children'), [Input('Hir_dropdown','value'),Input('Players','value')])
def update_graph_hir(challenge_selected, player_selected):
    istt = True
    type = 'Time'
    wrdff = allwrs.copy()
    if (challenge_selected == 'Glacier Park') | (challenge_selected == 'The Glacier Kicker'):
        istt = False
        type = 'Score'
    dff = hirdf.copy()
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
    
@app.callback(Output('challenge info','children'),Input('Hir_dropdown', 'value'))
def update_hir_info(challenge_selected):
    istt = True
    type = 'Time'
    if (challenge_selected == 'Glacier Park') | (challenge_selected == 'The Glacier Kicker'):
        istt = False
        type = 'Score'
    dff = hirdf.copy()
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

    return [html.H3(challenge_selected+" Info",
            style={'text-align': 'Center'}
            ),
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
    
if __name__ == '__main__':
	app.run_server(debug=True)
