# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 21:20:21 2022

@author: CZY
"""
import warnings                                  # do not disturbe mode
warnings.filterwarnings('ignore')

# Load packages

from helpFunc import *

import numpy as np                               # vectors and matrices
import pandas as pd                              # tables and data manipulations


from tqdm import trange

import pyomo.environ as pyo
from pyomo.opt import SolverFactory


def obj_rule(modelA):
      expr = 0
      for i in modelA.set_I:
        for r in modelA.set_R:
          for l in modelA.set_L:
            expr += modelA.Benefit[l]*modelA.x[i,r,l]*modelA.Freqs[i]
      return expr
  
def limitD(modelA,r,l):
     return sum(modelA.Cycles[i]*modelA.x[i,r,l] for i in modelA.set_I) <= modelA.Day
   
   
def limitx(modelA,i):
     return sum(modelA.x[i,r,l] for r in modelA.set_R for l in modelA.set_L) <= 1    
   
def runModelA(Day,rackNum,monthTrays,productSet):
        
    trayProduct = []
    trayFreq = []
    trayCycle = []
    
    for product in list(productSet.index):
        trayProduct.extend(monthTrays.loc[product]*[product])
        trayFreq.extend(monthTrays.loc[product]*[productSet.loc[product,'WaterFrequency [times/day]']])
        trayCycle.extend(monthTrays.loc[product]*[productSet.loc[product,'cycleLen']])
    
    trayProductDict = dict(zip(range(1,len(trayProduct)+1),trayProduct))
    trayFreqDict = dict(zip(range(1,len(trayFreq)+1),trayFreq))
    trayCycleDict = dict(zip(range(1,len(trayCycle)+1),trayCycle))
    
    shelfBenefitDict = dict(zip(range(1,11),reversed(range(1,11))))
    
 
    
    modelA = pyo.ConcreteModel("Plant Distribution")
    modelA.Day = pyo.Param(initialize=Day)
    modelA.rackNum = pyo.Param(initialize=rackNum)
    modelA.shelfNum = pyo.Param(initialize=10)
    modelA.trayNum = pyo.Param(initialize = np.sum(monthTrays))
    
    modelA.set_R = pyo.RangeSet(modelA.rackNum)
    modelA.set_L = pyo.RangeSet(modelA.shelfNum)
    modelA.productList = pyo.Set(initialize = list(productSet.index))
    modelA.set_I = pyo.RangeSet(modelA.trayNum)
    modelA.Freqs = pyo.Param(modelA.set_I,initialize = trayFreqDict)
    modelA.Cycles = pyo.Param(modelA.set_I,initialize = trayCycleDict)
    modelA.Benefit = pyo.Param(modelA.set_L,initialize = shelfBenefitDict)
    
    
    modelA.x= pyo.Var(modelA.set_I, modelA.set_R,modelA.set_L, within=pyo.Binary)
    
    # objective
    
    modelA.obj = pyo.Objective(rule = obj_rule, sense=pyo.maximize)
    
    # constraints
   
    
    modelA.c1 = pyo.Constraint(modelA.set_R, modelA.set_L, rule=limitD) 
    modelA.c2 = pyo.Constraint(modelA.set_I, rule = limitx)
    
    opt = SolverFactory('gurobi') 
    solution = opt.solve(modelA) # 调用求解器求解
    
    
    x_opt = np.array([pyo.value(modelA.x[i,r,l]) for i in modelA.set_I for r in modelA.set_R for l in modelA.set_L]).reshape((len(modelA.set_I), len(modelA.set_R),len(modelA.set_L))) # 提取最优解
  
    return x_opt

def get_rack_sol(x_opt,productSet,trayProduct):
    # For each shelf
    rack_sol = pd.DataFrame(index=range(x_opt.shape[1]),columns=range(x_opt.shape[2]))
    rack_freq = pd.DataFrame(index=range(x_opt.shape[1]),columns=range(x_opt.shape[2]))
    
    for r in range(x_opt.shape[1]):
        for l in range(x_opt.shape[2]):
            tmp =list( x_opt[:,r,l])
            tmpInd = find_indices(tmp, 1)
            
            if len(tmpInd) > 0:
                
                rlProduct = [trayProduct[i] for i in tmpInd]
                
                rlFreqCycle = [(productSet.loc[pd,'WaterFrequency [times/day]'],productSet.loc[pd,'cycleLen']) for pd in rlProduct]
                
                rlFreqCycle.sort(key = lambda item:item[0], reverse=True)
                rlFreq = [[freq]*rep for (freq,rep) in rlFreqCycle]
                rlFreq = [int(x) for item in rlFreq for x in item]
                
                rack_sol.iloc[r,l]=rlProduct
                rack_freq.iloc[r,l]=rlFreq
    
    
    
                
    # rack_sol.to_csv(r'D:\CZY\NeedCopy\UoE learning\Dissertation\code\farm_dataset\ShelfSol\rack_sol_rack25.csv')
    # rack_freq.to_csv(r'D:\CZY\NeedCopy\UoE learning\Dissertation\code\farm_dataset\ShelfSol\rack_freq_rack25.csv')
    
    # 获取每个rack第一天种植的product
   
    
    return rack_sol,rack_freq