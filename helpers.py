import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

import dash  # (version 1.12.0)
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import pathlib

PATH = pathlib.Path(__file__)
DATA_PATH = PATH.joinpath("../data").resolve()
challenges = pd.read_csv(DATA_PATH.joinpath("gmachallenges.csv"))
TDdf = pd.read_csv(DATA_PATH.joinpath("TDDF.csv"))
allwrs = pd.read_csv(DATA_PATH.joinpath("allwrs.csv"))
sortedwrs = pd.read_csv(DATA_PATH.joinpath("sortedwrs.csv"))
allpbs = pd.read_csv(DATA_PATH.joinpath("allpbs.csv"))

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

mountains_list = ['Hirschalm', 'Waldtal', 'Elnakka', 'Dalarna', 'Rotkamm', 'Saint Luvette',
                  'Passo Grolla', 'Ben Ailig', 'Mount Fairview', 'Pinecone Peaks']

# Fits score to exponential curve given two points
def calcHSpoints(x1,y1,x2,y2,score):
    gradient = (np.log(y2)-np.log(y1))/(x2-x1)
    intercept = np.log(y1)-(gradient*x1)
    return np.exp(intercept)*((np.exp(gradient))**score)

def get_challenge_names(mountain):
    mtddf = challenges[challenges['Mountain'] == mountain]
    return mtddf

def getTDcount(player):
    return int(TDdf[TDdf['Name'] == player].TD.iloc[0])

def recentWRs():
    wrdf = allwrs.copy()
    wrdf = wrdf.sort_values(by=['Timestamp'], ascending=False)
    return wrdf.head(10)

def recentPBs(playername):
    pbdf = allpbs[allpbs['Name'] == playername]
    pbdf = pbdf.sort_values(by=['Timestamp'], ascending=False)
    return pbdf.head(5)

# Returns png of challenge logo
def getchallengeImage(chaltype, width, height):
    if chaltype == 'Race':
        return html.Img(src=app.get_asset_url('challenge_gatetime.png'),style={'height':height, 'width':width})
    elif chaltype == 'Trail' or chaltype == 'Airtime' or chaltype == 'Long Jump' or chaltype == 'Slap' or chaltype == 'Single Trick' or chaltype == 'Single Drop':
        return html.Img(src=app.get_asset_url('challenge_trial.png'),style={'height':height, 'width':width})
    elif chaltype == 'TTB':
        return html.Img(src=app.get_asset_url('challenge_toptobottom_trial.png'),style={'height':height, 'width':width})
    elif chaltype == 'Distance':
        return html.Img(src=app.get_asset_url('challenge_distance.png'),style={'height':height, 'width':width})
    elif chaltype == 'Gated Trick':
        return html.Img(src=app.get_asset_url('challenge_gatetrick.png'),style={'height':height, 'width':width})
    elif chaltype == 'Open Trick':
        return html.Img(src=app.get_asset_url('challenge_timetrick.png'),style={'height':height, 'width':width})
    elif chaltype == 'Triple Drop':
        return html.Img(src=app.get_asset_url('challenge_drop.png'),style={'height':height, 'width':width})

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

# Converts milisecond value to string with proper formatting
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

# Returns Sum of Best for each mountain
def calcSumofBests():
    sum_of_bests = []
    sumdt = sortedwrs[sortedwrs['type'] != 'High score']
    for mountain in mountains_list:
        mtnsumdt = sumdt[sumdt['Mountain'] == mountain]
        sumofbest = (mtnsumdt['score'].sum())*1000
        sum_of_bests.append(convertMillisNoHours(int(sumofbest)))
    return sum_of_bests
