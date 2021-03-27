from typing import List
from fastapi import FastAPI, Query
import numpy_financial as npf
import numpy as np
from datetime import date
from math import ceil


getfired = FastAPI()


@getfired.get('/')
async def root():
    return( {'message': 'Please use an end point'})


@getfired.get('/eval')
async def eval_category(income: float, assets:float, retirement_expenses: float, expenses: float, savings: float, withdraw: float = 0.04, real_rate: float = 0.06):
    monthly_rate = 12 * ((1 + (real_rate)) ** (1. / 12) - 1)
    full_result = float(npf.nper(monthly_rate, -(income - expenses), -assets, retirement_expenses / withdraw))

    new_expenses = expenses - savings 
    result = full_result - float(npf.nper(monthly_rate, -(income - new_expenses), -assets, retirement_expenses / withdraw))

    return({'months saved' : result})


@getfired.get('/month')
async def eval_budget(income: float, assets:float, retirement_expenses: float, expenses: List[float] = Query([]), categories: List[str] = Query([]), withdraw: float = 0.04, real_rate: float = 0.06):
    monthly_rate = 12 * ((1 + (real_rate)) ** (1. / 12) - 1)
    result = float(npf.nper(monthly_rate, -(income - sum(expenses)), -assets, retirement_expenses / withdraw))

    time = {}
    for cat in categories:
        new_expenses = sum(expenses) - expenses[categories.index(cat)] 
        time[cat] = result - float(npf.nper(monthly_rate, -(income - new_expenses), -assets, retirement_expenses / withdraw))

    return({'months left' : result, 'categories' : time})


@getfired.get('/annual')
async def eval_budget(income: float, assets: float, curr_expenses: float, retirement_expenses: float, withdraw: float = 0.04, real_rate: float = 0.06):
    result = npf.nper(real_rate, -(income - curr_expenses), -assets, retirement_expenses / withdraw) * 12
    result_year = ceil(result / 12) 

    graph = np.empty((2, result_year))
    curr_year = date.today().year

    graph[0] = [curr_year + i for i in range(result_year)]
    graph[1] = npf.fv(real_rate, np.linspace(1, result_year, result_year), -(income - curr_expenses), -assets)

    return({'months left': result, 'graph' : graph.tolist()})
