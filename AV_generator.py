import numpy as np
import pandas as pd

#####SCORING FORMAT#####
pts_per_td = 6
pts_per_pass_td = 4
pts_per_yd = 0.1
pts_per_pass_yd = 0.04
pts_per_fum = 2
pts_per_int = 2

#####LEAGUE FORMAT#######
num_teams = 10
budget = 200
roster_size = 16
starting_qb = 1
starting_rb = 2
starting_wr = 2
starting_flex = 1
starting_te = 1
starting_d = 1
starting_k = 1
max_qb = 4
max_rb = 8
max_wr = 8
max_te = 3
max_d = 3
max_k = 3


#####RISK FACTOR#####
risk = 0.4

#####AVERAGE PLAYERS PER TEAM#####
avg_rb_per_team = 5.1
avg_wr_per_team = 5.6
avg_te_per_team = 1.5
avg_qb_per_team = 1.8

#####LOAD HISTORICAL DATA########
def load_data(position, year):
    x =  pd.read_pickle('Player_Data/' + position + "_" + year + ".pkl")
    fantasy(x)
    x.index.names = ['Player', 'Week']
    x = x.sort('Fan_Pts', ascending = False)
    return x
#####LOAD 2014 PROJECTIONS######    
def load_proj(position):
    if position == 'QB':
        col_headers = ['Player', 'Team', 'Pass_Att', 'Comp', 'Pass_Yds', 'Pass_Tds', 'Int', 'Rush_Att', 'Rush_Yds', 'Rush Tds', 'Fum', 'Fan_Pts']
        return pd.read_csv('Player_Data/' + 'FantasyPros_Fantasy_Football_Rankings_' + position + '.csv', sep='\t', names = col_headers, index_col = 'Player')
    if position == 'RB':
        col_headers = ['Player','Team','Rush_Att','Rush_Yds','Rush_TD','Rec_Att','Rec_Yds','Rec_TD', 'Fum', 'Fan_Pts'] 
        return pd.read_csv('Player_Data/' + 'FantasyPros_Fantasy_Football_Rankings_' + position + '.csv', sep='\t', names = col_headers, index_col = 'Player')
    if position == 'TE':
        col_headers = ['Player','Team','Rec_Att','Rec_Yds','Rec_TD','Fum','Fan_Pts']
        return pd.read_csv('Player_Data/' + 'FantasyPros_Fantasy_Football_Rankings_' + position + '.csv', sep='\t', names = col_headers, index_col = 'Player')
    if position == 'WR':
        col_headers = ['Player','Team','Rush_Att','Rush_Yds','Rush_TD','Rec_Att','Rec_Yds','Rec_TD','Fum','Fan_Pts'] 
        return pd.read_csv('Player_Data/' + 'FantasyPros_Fantasy_Football_Rankings_' + position + '.csv', sep='\t', names = col_headers, index_col = 'Player')



#####FUNCTION TO ADD FANTASY POINTS COLUMN######
def fantasy(df):
    
    if (df.columns.values == 'Fan_Pts').any():
        
        return
    
        
    elif (df.columns.values == 'Punt_Ret_TD').any():
        arr = np.empty(18)

        for i in range(0,18):
            arr = pts_per_td* df['Rec_TD'] + pts_per_yd* df['Rec_Yds'] + pts_per_td*df['Kickoff_TD'] + pts_per_td*df['Punt_Ret_TD'] - pts_per_fum*df['FumL']
        
        df['Fan_Pts'] = pd.Series(arr)
        
    elif (df.columns.values == 'Pass_TD').any():
        
        arr = pts_per_pass_td * df['Pass_TD'] + pts_per_td * df['Rush_TD'] + pts_per_pass_yd*df['Pass_Yds'] + pts_per_yd*df['Rush_Yds'] - pts_per_fum*df['FumL'] - pts_per_int*df['Int']
        df['Fan_Pts'] = pd.Series(arr)
    
    else:
    
        
        for i in range(0,18):
            arr = pts_per_td*df['Rec_TD'] + pts_per_td*df['Rush_TD'] + pts_per_yd*df['Rec_Yds'] + pts_per_yd*df['Rush_Yds']- pts_per_fum*df['FumL']
        df['Fan_Pts'] = pd.Series(arr)



####FUNCTION TO ADD VBD COLUMN#####

def vbd(df, num_starters, num_on_roster):
    
    if(df.columns.values == 'VBD').any():
        df = df.drop('VBD', 1)
        
    
    x = df['Fan_Pts']
    #baseline is the last player drafted (starters and bench) in each position on average
    baseline = x.values[num_on_roster*num_teams - 1]
    
    
    vbd= x - baseline
   
    vbd.sort(ascending = False)
    starters = vbd.head(num_teams * num_starters)
    starters = starters * (1 - risk)
    bench = vbd.tail(len(vbd) - num_teams * num_starters)
    bench = bench * risk
    df['VBD'] = starters.append(bench)



def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows') 




wr_2013 = load_data("WR", "2013")
rb_2013 = load_data("RB", "2013")
te_2013 = load_data("TE", "2013")
qb_2013 = load_data("QB", "2013")

flex_2013 = rb_2013.append(wr_2013)
flex_2013 = flex_2013.sort('Fan_Pts', ascending = False)

qb_proj = load_proj("QB")
rb_proj = load_proj("RB")
te_proj = load_proj("TE")
wr_proj = load_proj("WR")

vbd(rb_proj, starting_rb, avg_rb_per_team)
vbd(qb_proj, starting_qb, avg_qb_per_team)
vbd(wr_proj, starting_wr, avg_wr_per_team)
vbd(te_proj, starting_te, avg_te_per_team)

flex_proj = rb_proj.append(wr_proj)
flex_proj = flex_proj.sort(columns = 'Fan_Pts',ascending = False)



top_rb = rb_proj['VBD'].head(num_teams * starting_rb)
top_wr = wr_proj['VBD'].head(num_teams * starting_wr)
top_qb = qb_proj['VBD'].head(num_teams * starting_qb)
top_te= te_proj['VBD'].head(num_teams * starting_te)
top_flex = flex_proj['VBD'].head(num_teams * (starting_rb + starting_wr + starting_flex))
top_flex = top_flex[-top_flex.keys().isin(top_wr.keys() + top_rb.keys())]
avg = (top_rb.sum() + top_wr.sum() + top_te.sum() + top_qb.sum() + top_flex.sum())/num_teams 

std = 20
needed = avg + 1.29 * std



final_list = rb_proj['VBD'].append(qb_proj['VBD']).append(wr_proj['VBD']).append(te_proj['VBD'])
final_list = final_list * (budget/needed)
final_list.sort(ascending = False)
final_list[final_list < 1] = 1
print_full(final_list)
        
