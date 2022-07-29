# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 12:39:23 2022

@author: CZY
"""


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

#from modelAfunc import *
from BFD import *
# objective
def obj_rule(model):
  return sum(model.y[l] for l in model.set_L)
   

#  constraints
def limitD(model,l):
  return sum(model.Cycles[i]*model.z[i,l] for i in model.set_I) <= model.Day*model.y[l]


def limitx(model,i):
  return sum(model.z[i,l] for l in model.set_L) == 1

# 读取文件
folder = r'D:\CZY\NeedCopy\UoE learning\Dissertation\code\farm_dataset\allProduct\\'
productFile = folder+'productSet.csv'
traysFile = folder + 'demandTrays.csv'

productSetAll = pd.read_csv(productFile,index_col=["Product"])
demandTrays = pd.read_csv(traysFile,index_col=["Product"])
Days = [31,28,31,30,31,30,31,31,30,31,30,31]


# minimum racks
tray_list = []
rackNum = 100

for Month in range(12):
    Day = Days[Month]
    monthTraysAll = demandTrays["{}".format(Month+1)]
    productSet = productSetAll[monthTraysAll!=0]
    monthTrays = monthTraysAll[monthTraysAll!=0]    
    trayProduct = []
    # trayFreq = []
    trayCycle = []
    
 
    
    
    for product in list(productSet.index):
        trayProduct.extend(monthTrays.loc[product]*[product])
        # trayFreq.extend(monthTrays.loc[product]*[productSet.loc[product,'WaterFrequency [times/day]']])
        trayCycle.extend(monthTrays.loc[product]*[productSet.loc[product,'cycleLen']])
    
    trays = bfpack(trayCycle, Day)
    trays_num = len(trays)
    print("month {}: {} trays".format(Month+1,trays_num))
    
    
    trayProductDict = dict(zip(range(1,len(trayProduct)+1),trayProduct))
    # trayFreqDict = dict(zip(range(1,len(trayFreq)+1),trayFreq))
    trayCycleDict = dict(zip(range(1,len(trayCycle)+1),trayCycle))
    
    
    model = pyo.ConcreteModel("Minimum trays")
    model.Day = pyo.Param(initialize=Day)
    #model.rackNum = pyo.Param(initialize=rackNum)
    model.shelfNum = pyo.Param(initialize=rackNum*10)
    model.trayNum = pyo.Param(initialize = np.sum(monthTrays))
    
    #model.set_R = pyo.RangeSet(modelA.rackNum)
    model.set_L = pyo.RangeSet(model.shelfNum)
    model.productList = pyo.Set(initialize = list(productSet.index))
    model.set_I = pyo.RangeSet(model.trayNum)
    model.Cycles = pyo.Param(model.set_I,initialize = trayCycleDict)
    
    # variables
    model.z = pyo.Var(model.set_I, model.set_L, within=pyo.Binary)
    model.y = pyo.Var(model.set_L, within=pyo.Binary)
    

    model.obj = pyo.Objective(rule = obj_rule, sense=pyo.minimize)
    model.c1 = pyo.Constraint(model.set_L, rule=limitD) 
    model.c2 = pyo.Constraint(model.set_I, rule = limitx)

    opt = SolverFactory('gurobi') 
    solution = opt.solve(model) # 调用求解器求解

    obj_values = pyo.value(model.obj) # 提取目标函数
    print("month {}: {}".format(Month+1,obj_values))
    tray_list.append(obj_values)


# profit
profit_list = []
for Month in range(12):
    monthTraysAll = demandTrays["{}".format(Month+1)]
    # productSet = productSetAll[monthTraysAll!=0]
    # monthTrays = monthTraysAll[monthTraysAll!=0]  
    profit = np.dot(monthTraysAll, productSetAll['ProfitPerShelf'])
    profit_list.append(profit)
    