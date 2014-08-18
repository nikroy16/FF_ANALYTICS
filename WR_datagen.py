import sys
from lxml.html import parse
from urllib2 import urlopen
import numpy as np
import pandas as pd

year = sys.argv[1]
 
rows_per_player = 26

data = {}

for week in range(1,18):
    parsed = parse(urlopen('http://sports.yahoo.com/nfl/stats/byposition?pos=WR&conference=NFL&year=season_' + str(year) + '&timeframe=Week' + str(week) + '&sort=601&old_category=WR'))
    doc = parsed.getroot()
    links = doc.find_class('yspscores')
    np_links = np.array(links)
    raw_data = []
    for l in np_links:
        raw_data.append(l.text_content().replace(u'\xa0', ""))

   

    for text in raw_data:
            
        if text.replace(" ", "").replace(".", "").replace("'", "").replace("-", "").isalpha() and len(text) > 3:
        
            if data.has_key(text) == False:
                data[text] = {"Rec":dict.fromkeys(range(1,18)),"Tgt":dict.fromkeys(range(1,18)), "Rec_Yds":dict.fromkeys(range(1,18)), "Rec_Lng":dict.fromkeys(range(1,18)), "Rec_TD":dict.fromkeys(range(1,18)), "Kickoff_TD":dict.fromkeys(range(1,18)), "Punt_Ret_TD":dict.fromkeys(range(1,18)), "Fum":dict.fromkeys(range(1,18)), "FumL":dict.fromkeys(range(1,18)) }
                
    counter = -1
    for text in raw_data:
    
        counter = counter + 1
        
        mod = counter%rows_per_player
        
        if mod == 0:
            curr_player = text
            continue
        if mod == 1 or mod == 2 or mod == 3:
            continue;
        if mod == 4:
            data[curr_player]["Rec"][week] = float(text)
    
        if mod == 5:
            if text == "N/A":
                data[curr_player]["Tgt"][week] = 0.0
            else:
                data[curr_player]["Tgt"][week] = float(text)
    
        if mod== 6:
        
            data[curr_player]["Rec_Yds"][week] = float(text)

        if mod == 8:
            if text == "N/A":
                data[curr_player]["Rec_Lng"][week] = 0.0
            else:
                data[curr_player]["Rec_Lng"][week] = float(text)
    
        if mod == 9:
            
            data[curr_player]["Rec_TD"][week] = float(text)
            
                
    
        if mod == 15:
            
            data[curr_player]["Kickoff_TD"][week] = float(text)
            
            
        
        if mod == 21:
            data[curr_player]["Punt_Ret_TD"][week] = float(text)
        
        
        
        if mod == 23:
            data[curr_player]["Fum"][week] = float(text)
        
        if mod == 24:
            data[curr_player]["FumL"][week] = float(text)
        
      
        
def dict_operation(x):
    y = pd.Series(x)
    z = y.values
    x_sum = 0
    
    if len(z) == 17:
        x_sum = np.sum(y)
    else:
        x_sum = np.sum(y[1:])
    
    x[0] = x_sum
    return x 


df = pd.DataFrame(data).T

df = df.applymap(dict_operation)



x = df.to_dict()


playerIndex = []
weekIndex = []
for player in x['Fum']:
    
    playerIndex = playerIndex + ([player] * 18)
    weekIndex = weekIndex + range(0,18)
    
for stat in x:
    col = []
    for player in x[stat]:
        col = col + x[stat][player].values()
        
    x[stat] = col


    
    
df = pd.DataFrame(x, index = [playerIndex, weekIndex])

        
df.to_pickle('WR_' + year + '.pkl')
