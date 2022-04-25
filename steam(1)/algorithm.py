'''
Python 3
Software Engineering
Written By: Savannah Lopez and Nadia Morrow
Date Last Updated: 24/04/2022
This program creates an recommendation based off of a csv file of users and their interaction with games.
'''
#!/usr/bin/env python
# coding: utf-8

# # Steam Recommender System

# **Reading in the Steam dataset and libraries/packages**
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior() 
import os




# ## Data Loading and Exploration
steam_raw = pd.read_csv(r"C:\Users\nadia\TheNextGame\steam(1)\FinalDataSet.csv",usecols=[1,2,3,4],names=['userid','game','behavior','hoursplayed'])
steam_raw.head()
steam_raw.isnull().values.any()
steam_raw['userid'] = steam_raw.userid.astype(str)
steam_raw.describe()
gb = steam_raw.groupby('game')['userid'].nunique().sort_values(ascending=False).head()
ax = gb.plot(kind='bar', title='Number of players for Most Popular Games', ylabel='No. of players',
         xlabel='Game', figsize=(6, 5))
steam_df = steam_raw.copy()
steam_df = steam_df.iloc[1:]
steam_df["hoursplayed"] = steam_df["hoursplayed"].astype("float64", errors="ignore")
steam_df['like'] = [1 if x > 40.0 else 0 for x in steam_df['hoursplayed']]
steam_df['like'].value_counts()
steam_df.head()

bg=steam_df.groupby('game')['like'].apply(lambda x: (x==1).sum()).sort_values(ascending=False)
bg.head()
gb.head()
#Plot grouped bar-chart of common games
gbbg = pd.merge(gb, bg, on='game')
gbc = gbbg.plot.bar(logy=True)

# In[7]:


x = steam_df.groupby(['userid', 'game'])['behavior'].size()
s = x[x == 1]
len(s)
len(x)

boolean_index = steam_df.groupby(['userid','game'])['behavior'].transform('size') < 2
steam_df.loc[boolean_index,'hoursplayed'] = 0
steam_df.loc[steam_df['hoursplayed']==0]

steam_df.loc[steam_df.hoursplayed==0,'behavior'] = 'play'

steam_df.loc[steam_df['hoursplayed'] ==0]
steam_df = steam_df[steam_df.behavior != 'purchase']


d = {'like':'Sum Likes','hoursplayed':'Avg Hours Played'}
metrics_df = steam_df.groupby(['game'], as_index=False).agg({'like':'sum','hoursplayed':'mean'}).rename(columns=d)
metrics_df.loc[metrics_df['game'] == "Dota 2"] #Check Dota 2

c = metrics_df['Avg Hours Played'].mean()
#print("Average hours played across all games is " + str(round(c,2)))

m = metrics_df['Sum Likes'].quantile(0.95)
#print("Minimum number of likes for a game is " + str(m))

# In[9]:


metrics_df.shape
metrics_df = metrics_df.loc[metrics_df['Sum Likes'] >= m]
metrics_df.shape
metrics_df.head()




def weighted_rating(df, m=m, C=c):
    l = df['Sum Likes']
    a = df['Avg Hours Played']
    return (l/(l+m) * a) + (m/(l+m) * C)

metrics_df['score'] = metrics_df.apply(weighted_rating, axis=1)
metrics_df.head()

# In[11]:


metrics_df.index.name = 'index'
newIndex = metrics_df.sort_values(by=['score'],ascending=False).reset_index('index', drop=True)
newIndex.head(20)
newIndex.shape

# In[12]:

def gameInput(input):
    gameRec = input.__format__

        
userInput_df = pd.read_csv(r"C:\Users\nadia\TheNextGame\steam(1)\UserGameInput.txt", sep=",", usecols=[0], names=['game'])
userInput_df.head()

gameRec = userInput_df[userInput_df['game'].isin(newIndex['game'])]

#print (gameRec)

# In[25]:

#function that takes user input and returns the names of two games recommended
def getUserInput (input):
    gameInput = input
    location = newIndex.loc[newIndex['game'] == gameInput]
    #print (location)

    #metrics_df.loc[metrics_df['game'] == "Dota 2"] #Check Dota 2

    if  location.index == 0:
        t = 0
        re = newIndex.iloc[t: t+2]
        #print (re)
    
    #>>> df['date'][df.index[-1]]
    elif location.index == newIndex.index[newIndex.index[-1]]:
        t = newIndex['index'].iloc[-1]
        res = newIndex.iloc[t: t-2]
        #print(res)
    
    else :
        st = location.index.astype(int)
        result = newIndex.iloc[st+1]
        result2 = newIndex.iloc[st-1]
        return result['game'].loc[result.index[0]], result2['game'].loc[result2.index[0]]

#function that returns the names and score of the top 3 games
def getTopGames():
    return newIndex['game'].loc[newIndex.index[0]], newIndex['game'].loc[newIndex.index[1]],  newIndex['game'].loc[newIndex.index[2]], newIndex['score'].loc[newIndex.index[0]], newIndex['score'].loc[newIndex.index[1]], newIndex['score'].loc[newIndex.index[2]]