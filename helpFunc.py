# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 20:13:08 2022

@author: CZY
"""


import warnings                                  
warnings.filterwarnings('ignore')

# Load packages
import numpy as np                               
import pandas as pd    


    
    
 
def getFirstDay(freqList):
    if (type(freqList) == list) and (len(freqList)>0):
        return freqList[0]
    else:
        return np.nan



def get_rounds_time(productSet,rack_freq_firstday):
    aveWaterTime = np.mean(productSet['WaterEach(L/time)'])*1.5
    #rack_rounds = pd.DataFrame(index=set_R,columns = set_L)
    set_R = range(rack_freq_firstday.shape[0])
    set_L = range(rack_freq_firstday.shape[1])
    set_F = range(max(productSet['WaterFrequency [times/day]']))
    rack_rounds_time = pd.DataFrame(index=set_R,columns = set_F)
    for r in set_R:
        rFreqList = list(rack_freq_firstday.loc[r,:].fillna(0))
        rounds = [(rFreqList[k]-max(rFreqList[k+1:])) for k in range(9)]
        rounds = [item if item >=0 else 0 for item in rounds]
        rounds.append(rFreqList[-1])
        #rack_rounds.loc[r,:]=rounds
        rounds_time = []
        
        for l in set_L:

            rounds_time.append(int(rounds[l])*[l*10+(l+1)*aveWaterTime])
        rounds_time = [x for item in rounds_time for x in item]
        
        rounds_time.extend(0 for k in range(abs(len(set_F)-len(rounds_time))))
        rounds_time.sort(reverse=True)
        rack_rounds_time.loc[r,:] = rounds_time
    return rack_rounds_time

def get_light_time(productSet,rack_freq_firstday):
    aveLightTime = np.mean(productSet['LuxTotal'])/2500
    set_R = range(rack_freq_firstday.shape[0])
    rack_rounds_light_time = pd.Series(index = set_R)
    for r in set_R:
        notnan = len(rack_freq_firstday.iloc[r,:])-np.isnan(rack_freq_firstday.iloc[r,:]).sum()
        rack_rounds_light_time[r]= notnan*aveLightTime + (notnan-1)*10
    return rack_rounds_light_time

