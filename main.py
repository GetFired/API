from typing import List
from fastapi import FastAPI, Query
import numpy_financial as npf
import numpy as np
from datetime import date
from math import ceil


getfired = FastAPI()

# https://www.macrotrends.net/2526/sp-500-historical-annual-returns 1950 and beyond
sp_500 = {1950: 0.21780000000000002, 1951: 0.1646, 1952: 0.11779999999999999, 1953: -0.0662, 1954: 0.45020000000000004, 1955: 0.264, 1956: 0.0262, 1957: -0.1431, 1958: 0.38060000000000005, 1959: 0.0848, 1960: -0.0297, 1961: 0.23129999999999998, 1962: -0.11810000000000001, 1963: 0.1889, 1964: 0.1297, 1965: 0.0906, 1966: -0.1309, 1967: 0.2009, 1968: 0.0766, 1969: -0.11359999999999999, 1970: 0.001, 1971: 0.1079, 1972: 0.1563, 1973: -0.17370000000000002, 1974: -0.29719999999999996, 1975: 0.3155, 1976: 0.19149999999999998, 1977: -0.115, 1978: 0.0106, 1979: 0.1231, 1980: 0.2577, 1981: -0.0973, 1982: 0.1476, 1983: 0.1727, 1984: 0.013999999999999999, 1985: 0.2633, 1986: 0.1462, 1987: 0.0203, 1988: 0.124, 1989: 0.2725, 1990: -0.06559999999999999, 1991: 0.2631, 1992: 0.0446, 1993: 0.0706, 1994: -0.0154, 1995: 0.3411, 1996: 0.2026, 1997: 0.31010000000000004, 1998: 0.2667, 1999: 0.1953, 2000: -0.1014, 2001: -0.1304, 2002: -0.23370000000000002, 2003: 0.2638, 2004: 0.08990000000000001, 2005: 0.03, 2006: 0.1362, 2007: 0.0353, 2008: -0.3849, 2009: 0.2345, 2010: 0.1278, 2011: 0.0, 2012: 0.1341, 2013: 0.29600000000000004, 2014: 0.1139, 2015: -0.0073, 2016: 0.09539999999999998, 2017: 0.1942, 2018: -0.062400000000000004, 2019: 0.2888, 2020: 0.16260000000000002, 2021: 0.0409}

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


@getfired.get('/historical')
async def eval_budget(income: float, assets: float, curr_expenses: float, retirement_expenses: float, withdraw: float = 0.04):
    goal = retirement_expenses / withdraw
    start_year = 1950
    curr_year = date.today().year
    length = []

    for i in range(75):
        init = np.random.randint(start_year, curr_year - 10)
        fv = assets       
        counter = 0
        interest = []
        while fv < goal and counter + init < curr_year:
            if(sp_500[init + counter] != 0):
                fv = npf.fv(sp_500[init + counter], 1, -(income - curr_expenses), -fv)
            interest.append(sp_500[init + counter])
            counter += 1

        if(fv >= goal):
            length.append(counter)

    return({'average_years' : sum(length) / len(length)})
