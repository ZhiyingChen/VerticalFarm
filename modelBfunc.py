# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 19:57:09 2022

@author: CZY
"""
import warnings                                  # do not disturbe mode
warnings.filterwarnings('ignore')

# Load packages

from helpFunc import *

import numpy as np                               # vectors and matrices
import pandas as pd                              # tables and data manipulations
import matplotlib.pyplot as plt                  # plots
import seaborn as sns   


from tqdm import trange

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# objective
def objFunc(model):
  return sum(model.y_up[w] for w in model.set_W )+ sum(model.y_down[u] for u in model.set_U)


# Constraints
def c5_rule(model,w,s):
  return sum(model.tw[r,v]*model.x_up[r,v,w,s] for r in model.set_R for v in model.set_V) <= model.hw*model.y_up[w]

def c6_rule(model,u,s):
  return sum(model.tu[r]*model.x_down[r,u,s] for r in model.set_R) <= model.hu*model.y_down[u]

def c7_rule(model,r,v):
  return sum(model.x_up[r,v,w,s] for w in model.set_W for s in model.set_Sw)==1

def c8_rule(model,r):
  return sum(model.x_down[r,u,s] for u in model.set_U for s in model.set_Su)==1

def runModelB(productSet,rack_rounds_time,rack_rounds_light_time):
    # 建立第二个模型
    # 准备参数
    
    vNum = max(productSet['WaterFrequency [times/day]'])
    rackNum = rack_rounds_time.shape[0]
    
    possible_wbot = int(np.sum(np.sum(rack_rounds_time))/(16*60))*2
    possible_lbot = int(np.sum(rack_rounds_light_time)/(15*60))*5
    
    
    
    hw = 2*60
    hu = 3*60
    
    tw = np.array(rack_rounds_time)
    tu = np.array(rack_rounds_light_time)
    
    
    
    twDict = {}
    for r in range(tw.shape[0]):
      for v in range(tw.shape[1]):
        twDict[(r+1,v+1)]=tw[r][v]
    
    tuDict = dict(zip(range(1,len(tu)+1),tu))
    # 建模
    
    model = pyo.ConcreteModel()
    
    model.set_W = pyo.RangeSet(possible_wbot)
    model.set_U = pyo.RangeSet(possible_lbot)
    model.set_Sw = pyo.RangeSet(8)
    model.set_Su = pyo.RangeSet(5)
    model.set_V = pyo.RangeSet(vNum)
    model.set_R = pyo.RangeSet(rackNum)
    
    model.hw = pyo.Param(initialize = 2*60)
    model.hu = pyo.Param(initialize = 3*60)
    
    model.tw = pyo.Param(model.set_R, model.set_V, initialize = twDict)
    model.tu = pyo.Param(model.set_R, initialize = tuDict)
    
    # variables
    model.x_up = pyo.Var(model.set_R, model.set_V, model.set_W, model.set_Sw, within = pyo.Binary)
    model.x_down = pyo.Var(model.set_R, model.set_U, model.set_Su, within = pyo.Binary)
    model.y_up = pyo.Var(model.set_W, within = pyo.Binary)
    model.y_down = pyo.Var(model.set_U, within = pyo.Binary)
    
    # objective
    model.obj = pyo.Objective(rule = objFunc, sense = pyo.minimize) 
    
    # Constraints
    model.c5 = pyo.Constraint(model.set_W, model.set_Sw, rule = c5_rule)
    
    model.c6 = pyo.Constraint(model.set_U, model.set_Su, rule = c6_rule)
    
    
    model.c7 = pyo.Constraint(model.set_R, model.set_V, rule = c7_rule)
    
    
    model.c8 = pyo.Constraint(model.set_R, rule = c8_rule)
    
    opt = SolverFactory('gurobi') # 指定 gurobi 作为求解器
    # opt = SolverFactory('cplex') # 指定 cplex 作为求解器
    # opt = SolverFactory('scip') # 指定 scip 作为求解器
    solution = opt.solve(model) # 调用求解器求解
    
    y_up_opt = np.array([pyo.value(model.y_up[w]) for w in model.set_W])
    y_down_opt = np.array([pyo.value(model.y_down[u]) for u in model.set_U])    
                        
    wbot_num = np.sum(y_up_opt)
    lbot_num = np.sum(y_down_opt)
     
    # obj_values = pyo.value(model.obj) # 提取最优目标函数值
    return wbot_num, lbot_num

