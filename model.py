


import warnings                                  # do not disturbe mode
warnings.filterwarnings('ignore')

# Load packages

from InterChangeFunc import getPdShelfCost,getFirstDay,get_dec_rate,get_rounds_time,get_light_time,find_indices


import numpy as np                               # vectors and matrices
import pandas as pd                              # tables and data manipulations
import matplotlib.pyplot as plt                  # plots
import seaborn as sns   


from tqdm import trange,tqdm

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

from modelAfunc import *
from modelBfunc import *
# 读取文件
#folder = r'D:\CZY\NeedCopy\UoE learning\Dissertation\code\farm_dataset\allProduct\\'

productFile = 'productSet.csv'
traysFile = 'demandTrays.csv'

productSetAll = pd.read_csv(productFile,index_col=["Product"])
demandTrays = pd.read_csv(traysFile,index_col=["Product"])

robotRentPerDay = 5
botCostPerMin = robotRentPerDay/(24*60)
penaltyPerShelf = botCostPerMin*10

rackNum = 100

Days = [31,28,31,30,31,30,31,31,30,31,30,31]
# 定义参数
Month = 2

for Month in trange(1,13):
    Day = Days[Month-1]
    monthTraysAll = demandTrays["{}".format(Month)]
    
    

    
    
    productSet = productSetAll[monthTraysAll!=0]
    monthTrays = monthTraysAll[monthTraysAll!=0]
    
    
    x_opt = runModelA(Day,rackNum,monthTrays,productSet)   
  
    rack_sol,rack_freq = get_rack_sol(x_opt,productSet,trayProduct)
    
    rack_freq_firstday = rack_freq.copy(deep=True)
    rack_freq_firstday = rack_freq_firstday.applymap(getFirstDay)
    
    #result_folder = r'D:\CZY\NeedCopy\UoE learning\Dissertation\code\farm_dataset\Results\Rack'+str(rackNum)
    #rack_sol.to_csv(result_folder+'\\rack_sol_month'+str(Month)+'.csv')
    #rack_freq.to_csv(result_folder+'\\rack_freq_month'+str(Month)+'.csv')
    #rack_freq_firstday.to_csv(result_folder+'\\rack_freq_firstday_month'+str(Month)+'.csv')
    
    wbot_num, lbot_num = runModelB(productSet,rack_rounds_time,rack_rounds_light_time)
        
        
    robot_num +=  wbot_num + lbot_num
    robot_cost += (robot_num)*14*Day
    rdic = {"rackNum":rackNum, "Month": Month ,"supposed_income":income[Month-1],"income":month_income,"empty":month_empty,"wbot": wbot,"lbot": lbot, "cost": robot_cost}
    robots  = robots.append(pd.DataFrame([rdic]))