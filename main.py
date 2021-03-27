from pydantic import BaseModel
from fastapi import FastAPI
import numpy_financial as npf
import numpy as np
from datetime import date
from math import ceil


getfired = FastAPI()


@getfired.get('/')
async def root():
    return( {'message': 'Hello World'})

#monthly_rate = 12 * ((1 + (real_rate)) ** (1. / 12) - 1)

@getfired.get('/budget')
async def eval_budget(income: float, assets: float, curr_expenses: float, retirement_expenses: float, withdraw: float = 0.04, real_rate: float = 0.06):
    result = npf.nper(real_rate, -(income - curr_expenses), -assets, retirement_expenses / withdraw) * 12
    result_year = ceil(result / 12) 

    graph = np.empty((2, result_year))
    curr_year = date.today().year

    graph[0] = [curr_year + i for i in range(result_year)]
    graph[1] = npf.fv(real_rate, np.linspace(1, result_year, result_year), -(income - curr_expenses), -assets)

    print(graph)

    return( {'months left': result, 'graph' : graph.tolist()} )
