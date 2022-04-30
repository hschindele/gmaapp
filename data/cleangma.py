import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

numTTTDs = 180
numHSTDs = 86
chals = pd.read_csv('gmachallenges.csv')
df = pd.read_csv('gmaraw.csv')
df = df[df['Verified?'] == "Yes"]
df = df.replace(np.nan, '', regex=True)
df['challenge name'] = df["Select TT Challenge"] + df["Select HS Challenge"]
df['type'] = df["Challenge Type "] + df["Challenge Type"]
df['score'] = df["Enter score as just a number"].astype(str) + df["Enter time as (sec).(mil) EX: 62.69"].astype(str)
df = df.drop(['Select TT Challenge','Select HS Challenge','Challenge Type ','Challenge Type','Enter score as just a number','Enter time as (sec).(mil) EX: 62.69','Enter Mountain Score'], axis=1)

for i in range(1,11):
	ttstring = "Select TT Challenge."+str(i)
	hsstring = "Select HS Challenge."+str(i)
	ttscore = "Enter time as (sec).(mil) EX: 62.69."+str(i)
	hsscore = "Enter score as just a number."+str(i)
	df['challenge name'] = df['challenge name'] + df[ttstring] + df[hsstring]
	df['score'] = df['score'] + df[ttscore].astype(str) + df[hsscore].astype(str)
	df = df.drop([ttscore, hsscore, ttstring, hsstring], axis = 1)

for i in range(1,10):
	challengestring = "Challenge Type."+str(i)
	df['type'] = df['type'] + df[challengestring]
	df = df.drop([challengestring], axis=1)

for i in range(1,7):
	mtnstring = "Enter Mountain Score."+str(i)
	df = df.drop([mtnstring], axis=1)

df = df.rename(columns={"Upload screenshot verification":"Link", "Write your name exactly as you want it to be displayed":"Name", "Was this run on iOS or Android?":"OS", "What mountain is your run for?":"Mountain"})

df['score'] = pd.to_numeric(df.score)
tt = df[(df['type'] == 'Time trial') | (df['type'] == 'Time Trial')]
hs = df[(df['type'] == 'High score') | (df['type'] == 'High Score')]
ttchallengenames = tt['challenge name'].unique()
hschallengenames = hs['challenge name'].unique()

df['chaltype'] = ''
ind = 0
for chalname in df['challenge name']:
    chalrow = chals[chals['Challenge Name'] == chalname].iloc[0]
    df['chaltype'].iloc[ind] = chalrow.chaltype
    ind += 1
    
ttwrs = pd.DataFrame()
hswrs = pd.DataFrame()
allwrs = pd.DataFrame()

for chalname in ttchallengenames:
    curdf = df[df['challenge name'] == chalname]
    score = curdf['score'].min()
    wrrow = curdf.loc[(curdf['score'] == score) & (curdf['challenge name'] == chalname)]
    mindate = wrrow['Timestamp'].min()
    wrrow = wrrow[wrrow['Timestamp'] == mindate]
    allwrs = pd.concat([allwrs,wrrow])
    ttwrs = pd.concat([ttwrs,wrrow])

for chalname in hschallengenames:
    curdf = df[df['challenge name'] == chalname]
    curdf['score'] = pd.to_numeric(curdf.score)
    score = curdf['score'].max()
    wrrow = curdf.loc[(curdf['score'] == score) & (curdf['challenge name'] == chalname)]
    allwrs = pd.concat([allwrs,wrrow])
    hswrs = pd.concat([hswrs,wrrow])




df.to_csv('out.csv', index=False)
ttwrs.to_csv('ttwrs.csv', index=False)
hswrs.to_csv('hswrs.csv', index=False)
allwrs.to_csv('allwrs.csv', index=False)

clean = pd.read_csv('out.csv', index_col=1)
cleanhir = clean[(clean['Mountain'] == "Hirschalm") & (clean['challenge name'] != "")]
cleanwal = clean[(clean['Mountain'] == "Waldtal") & (clean['challenge name'] != "")]
cleaneln = clean[(clean['Mountain'] == "Elnakka") & (clean['challenge name'] != "")]
cleandal = clean[(clean['Mountain'] == "Dalarna") & (clean['challenge name'] != "")]
cleanrot = clean[(clean['Mountain'] == "Rotkamm") & (clean['challenge name'] != "")]
cleansai = clean[(clean['Mountain'] == "Saint Luvette") & (clean['challenge name'] != "")]
cleanpas = clean[(clean['Mountain'] == "Passo Grolla") & (clean['challenge name'] != "")]
cleanben = clean[(clean['Mountain'] == "Ben Ailig") & (clean['challenge name'] != "")]
cleanmou = clean[(clean['Mountain'] == "Mount Fairview") & (clean['challenge name'] != "")]
cleanpin = clean[(clean['Mountain'] == "Pinecone Peaks") & (clean['challenge name'] != "")]
cleanagp = clean[(clean['Mountain'] == "Agpat Island") & (clean['challenge name'] != "")]
cleanhir.to_csv('hirschalm.csv', index=False)
cleanwal.to_csv('waldtal.csv', index=False)
cleaneln.to_csv('elnakka.csv', index=False)
cleandal.to_csv('dalarna.csv', index=False)
cleanrot.to_csv('rotkamm.csv', index=False)
cleansai.to_csv('saint luvette.csv', index=False)
cleanpas.to_csv('passo grolla.csv', index=False)
cleanben.to_csv('ben ailig.csv', index=False)
cleanmou.to_csv('mount fairview.csv', index=False)
cleanpin.to_csv('pinecone peaks.csv', index=False)
cleanagp.to_csv('agpat island.csv', index=False)

allpbs = pd.DataFrame()
print("Making PB Sheet")
for chalname in chals['Challenge Name']:
    cleancopy = clean[clean['challenge name'] == chalname]
    if not cleancopy.empty:
        if cleancopy['type'].iloc[0] == 'High score':
            chalpbs = cleancopy.set_index(['Timestamp','type','OS','challenge name','Mountain']).groupby('Name')['score'].nlargest(1).reset_index(name='score')
            allpbs = allpbs.append(chalpbs)
        else:
            chalpbs = cleancopy.set_index(['Timestamp','type','OS','challenge name','Mountain']).groupby('Name')['score'].nsmallest(1).reset_index(name='score')
            allpbs = allpbs.append(chalpbs)
    else:
        print(chalname+" not found")

ind = 0
for timestamp in allpbs['Timestamp']:
    currowsub = clean[clean['Timestamp'] == timestamp].iloc[0]
    allpbs['Name'].iloc[ind] = currowsub['Name']
    ind += 1


def calcHSpoints(x1,y1,x2,y2,score):
    gradient = (np.log(y2)-np.log(y1))/(x2-x1)
    intercept = np.log(y1)-(gradient*x1)
    return np.exp(intercept)*((np.exp(gradient))**score)

print("Calculating PB Scores")
allpbs['Points'] = 0
ind = 0
for score in allpbs['score']:
    points = 0
    curchal = allpbs['challenge name'].iloc[ind]
    curchaldf = chals[chals['Challenge Name'] == curchal].iloc[0]
    if curchaldf['type'] == 'High Score':
        if curchaldf['TD'] > 1:
            wr = float(allwrs[allwrs['challenge name'] == curchal].score.iloc[0])
            points = int(calcHSpoints(curchaldf['TD'], 10000, wr, 20000, score))+1
            #print('Name: '+curchal+' TD: '+str(curchaldf['TD'])+' WR: '+str(wr)+' score: '+str(score)+' points: '+str(points))
            if points < 0:
                points = 0
        else:
            points = 0
    else:
        if curchaldf['TD'] > score:
            points = int(10000*((curchaldf['TD'] - score)+1))
        else:
            points = int(625*(2**((4*(curchaldf['DD']) - 3*curchaldf['TD'] -score)/(curchaldf['DD']-curchaldf['TD']))))
    allpbs['Points'].iloc[ind] = points
    ind += 1


allpbs.to_csv('allpbs.csv', index=False)

print("Making Point Ranking Table")
allptrank = allpbs.groupby('Name')['Points'].sum().reset_index()
allttrank = allpbs[allpbs['type'] != 'High score'].groupby('Name')['Points'].sum().reset_index()
allhsrank = allpbs[allpbs['type'] == 'High score'].groupby('Name')['Points'].sum().reset_index()
allptrank = allptrank.sort_values('Points', ascending=False).reset_index(drop=True)
allttrank = allttrank.sort_values('Points', ascending=False).reset_index(drop=True)
allhsrank = allhsrank.sort_values('Points', ascending=False).reset_index(drop=True)
allptrank.index = allptrank.index.set_names(['Rank'])
allttrank.index = allttrank.index.set_names(['Rank'])
allhsrank.index = allhsrank.index.set_names(['Rank'])
allptrank.to_csv('totalrank.csv', index='Points')
allttrank.to_csv('totalttrank.csv', index='Points')
allhsrank.to_csv('totalhsrank.csv', index='Points')

ttpbs = allpbs[allpbs['type'] != 'High score']
hspbs = allpbs[allpbs['type'] == 'High score']

mountain_prefixes = [('Hirschalm','hir'),('Waldtal','wal'),('Elnakka','eln'),('Dalarna','dal'),
                     ('Rotkamm', 'rot'), ('Saint Luvette', 'sai'), ('Passo Grolla', 'pas'),
                     ('Ben Ailig', 'ben'), ('Mount Fairview','fai'), ('Pinecone Peaks','pin'), ('Agpat Island','agp')]

allpbs[allpbs['Points'] > 10000] = allpbs[allpbs['Points'] > 10000].round({'Points':-2})

sortedwrs = allwrs.head(1)
for index, pair in enumerate(mountain_prefixes):
    mountainoverall = allpbs[allpbs['Mountain'] == pair[0]].groupby('Name')['Points'].sum().reset_index()
    mountaintt = ttpbs[ttpbs['Mountain'] == pair[0]].groupby('Name')['Points'].sum().reset_index()
    mountainhs = hspbs[hspbs['Mountain'] == pair[0]].groupby('Name')['Points'].sum().reset_index()
    mountainoverall = mountainoverall.sort_values('Points', ascending=False).reset_index(drop=True)
    mountaintt = mountaintt.sort_values('Points', ascending=False).reset_index(drop=True)
    mountainhs = mountainhs.sort_values('Points', ascending=False).reset_index(drop=True)
    overallstring = pair[1]+"overallrank.csv"
    ttstring = pair[1]+"ttrank.csv"
    hsstring = pair[1]+"hsrank.csv"
    mountainoverall.index = mountainoverall.index.set_names(['Rank'])
    mountaintt.index = mountaintt.index.set_names(['Rank'])
    mountainhs.index = mountainhs.index.set_names(['Rank'])
    mountainoverall.to_csv(overallstring)
    mountaintt.to_csv(ttstring)
    mountainhs.to_csv(hsstring)
    
    wrcopy = allwrs[allwrs['Mountain'] == pair[0]].copy()
    wrtt = wrcopy[wrcopy['type'] != 'High score']
    wrhs = wrcopy[wrcopy['type'] == 'High score']
    sortedwrs = sortedwrs.append(wrtt)
    sortedwrs = sortedwrs.append(wrhs)

sortedwrs = sortedwrs.reset_index()
sortedwrs = sortedwrs.iloc[1:]
sortedwrs.to_csv('sortedwrs.csv')

print('Creating Achievements')

achievementsdf = pd.DataFrame(columns = ['Name','Award','Importance'])
overallchamp = allptrank.Name.iloc[0]
ttchamp = allttrank.Name.iloc[0]
hschamp = allhsrank.Name.iloc[0]
achievementsdf = achievementsdf.append([{'Name':overallchamp,'Award':'#1 Overall Rating','Importance':1}])
achievementsdf = achievementsdf.append([{'Name':ttchamp,'Award':'#1 Time Trial Rating','Importance':2}])
achievementsdf = achievementsdf.append([{'Name':hschamp,'Award':'#1 High Score Rating','Importance':2}])
#Make tt hs and overall Champs
for i in range(1,5):
    overalltopfive = allptrank.Name.iloc[i]
    tttopfive = allttrank.Name.iloc[i]
    hstopfive = allhsrank.Name.iloc[i]
    achievementsdf = achievementsdf.append([{'Name':overalltopfive,'Award':'Top 5 Overall Rating','Importance':3}])
    achievementsdf = achievementsdf.append([{'Name':tttopfive,'Award':'Top 5 Time Trial Rating','Importance':4}])
    achievementsdf = achievementsdf.append([{'Name':hstopfive,'Award':'Top 5 High Score Rating','Importance':4}])
    
#Make top 6 through 10
for i in range(5,10):
    overalltopten = allptrank.Name.iloc[i]
    tttopten = allttrank.Name.iloc[i]
    hstopten = allhsrank.Name.iloc[i]
    achievementsdf = achievementsdf.append([{'Name':overalltopten,'Award':'Top 10 Overall Rating','Importance':7}])
    achievementsdf = achievementsdf.append([{'Name':tttopten,'Award':'Top 10 Time Trial Rating','Importance':8}])
    achievementsdf = achievementsdf.append([{'Name':hstopten,'Award':'Top 10 High Score Rating','Importance':8}])

#Make Challenge Champions
challengetypes = sortedwrs['chaltype'].unique()
for challengetype in challengetypes:
    chalwrs = sortedwrs[sortedwrs['chaltype'] == challengetype]
    mostcommonname = chalwrs['Name'].value_counts().idxmax()
    achievementsdf = achievementsdf.append([{'Name':mostcommonname,'Award':challengetype+' Champion','Importance':6}])

#Make Mountain Champions
for index, pair in enumerate(mountain_prefixes):
    monoveralldf = pd.read_csv(pair[1]+'overallrank.csv')
    monttdf = pd.read_csv(pair[1]+'ttrank.csv')
    monhsdf = pd.read_csv(pair[1]+'hsrank.csv')
    monoverallchamp = monoveralldf.Name.iloc[0]
    monttchamp = monttdf.Name.iloc[0]
    monhschamp = monhsdf.Name.iloc[0]
    achievementsdf = achievementsdf.append([{'Name':monoverallchamp,'Award':pair[0]+' Overall Champion','Importance':9}])
    achievementsdf = achievementsdf.append([{'Name':monttchamp,'Award':pair[0]+' Time Trial Champion','Importance':10}])
    achievementsdf = achievementsdf.append([{'Name':monhschamp,'Award':pair[0]+' High Score Champion','Importance':10}])

for name in sortedwrs.Name.unique():
    achievementsdf = achievementsdf.append([{'Name':name,'Award':'World Record Holder','Importance':11}])

print('Making TD Table')

tddf = allpbs.copy()
tddf['TD'] = False
tddf['TTTD'] = False
tddf['HSTD'] = False
ind = 0
for score in tddf.score:
    chalname = tddf['challenge name'].iloc[ind]
    curchalrow = chals[chals['Challenge Name'] == chalname].iloc[0]
    if tddf['type'].iloc[ind] != 'High score':
        if tddf['score'].iloc[ind] < curchalrow.TD:
            tddf['TD'].iloc[ind] = True
            tddf['TTTD'].iloc[ind] = True
    else:
        if tddf['score'].iloc[ind] > curchalrow.TD:
            tddf['TD'].iloc[ind] = True
            tddf['HSTD'].iloc[ind] = True
    ind += 1

fulltddf = tddf.groupby('Name')['TD','TTTD','HSTD'].sum()

fulltddf.to_csv('TDDF.csv')
fulltddf = fulltddf.reset_index()

ind = 0
for numTDs in fulltddf['TD']:
    if numTDs == (numTTTDs+numHSTDs):
        name = fulltddf['Name'].iloc[ind]
        achievementsdf = achievementsdf.append([{'Name':name,'Award':'Grand Mountain Master','Importance':3}])
    ind += 1
ind = 0
for numTDs in fulltddf['TTTD']:
    if numTDs == numTTTDs:
        name = fulltddf['Name'].iloc[ind]
        achievementsdf = achievementsdf.append([{'Name':name,'Award':'Speedy Boi','Importance':4}])
    ind += 1
ind = 0
for numTDs in fulltddf['HSTD']:
    if numTDs == numHSTDs:
        name = fulltddf['Name'].iloc[ind]
        achievementsdf = achievementsdf.append([{'Name':name,'Award':'Stomper','Importance':4}])
    ind += 1

achievementsdf.to_csv('achievments.csv')
