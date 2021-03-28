from typing import List
from fastapi import FastAPI, Query
import numpy_financial as npf
import numpy as np
from datetime import date
from math import ceil

# TODO turn fire date calculator into a function call

getfired = FastAPI()

# https://www.macrotrends.net/2526/sp-500-historical-annual-returns 1950 and beyond
sp_500 = {1950: 0.21780000000000002, 1951: 0.1646, 1952: 0.11779999999999999, 1953: -0.0662, 1954: 0.45020000000000004, 1955: 0.264, 1956: 0.0262, 1957: -0.1431, 1958: 0.38060000000000005, 1959: 0.0848, 1960: -0.0297, 1961: 0.23129999999999998, 1962: -0.11810000000000001, 1963: 0.1889, 1964: 0.1297, 1965: 0.0906, 1966: -0.1309, 1967: 0.2009, 1968: 0.0766, 1969: -0.11359999999999999, 1970: 0.001, 1971: 0.1079, 1972: 0.1563, 1973: -0.17370000000000002, 1974: -0.29719999999999996, 1975: 0.3155, 1976: 0.19149999999999998, 1977: -0.115, 1978: 0.0106, 1979: 0.1231, 1980: 0.2577, 1981: -0.0973, 1982: 0.1476, 1983: 0.1727, 1984: 0.013999999999999999, 1985: 0.2633, 1986: 0.1462, 1987: 0.0203, 1988: 0.124, 1989: 0.2725, 1990: -0.06559999999999999, 1991: 0.2631, 1992: 0.0446, 1993: 0.0706, 1994: -0.0154, 1995: 0.3411, 1996: 0.2026, 1997: 0.31010000000000004, 1998: 0.2667, 1999: 0.1953, 2000: -0.1014, 2001: -0.1304, 2002: -0.23370000000000002, 2003: 0.2638, 2004: 0.08990000000000001, 2005: 0.03, 2006: 0.1362, 2007: 0.0353, 2008: -0.3849, 2009: 0.2345, 2010: 0.1278, 2011: 0.0, 2012: 0.1341, 2013: 0.29600000000000004, 2014: 0.1139, 2015: -0.0073, 2016: 0.09539999999999998, 2017: 0.1942, 2018: -0.062400000000000004, 2019: 0.2888, 2020: 0.16260000000000002, 2021: 0.0409}

@getfired.get('/')
async def root():
    return( {'message': 'Please use an end point'})


@getfired.get('/eval')
async def eval_category(income: float, assets:float, retirement_expenses: float, expenses: float, savings: float, withdraw: float = 0.04, real_rate: float = 0.06, income_growth: float = 0.05):
    monthly_rate = (1 + (real_rate)) ** (1. / 12) - 1
    fv = assets
    goal = retirement_expenses / withdraw
    original_month = 0
    scaled_income = income

    while fv < goal:
        fv = npf.fv(monthly_rate, 1, -(scaled_income - expenses), -fv)

        original_month += 1
        scaled_income = scaled_income * (1 + income_growth / 12)
    
    new_expenses = expenses - savings 
    month = 0
    fv = assets
    scaled_income = income

    while fv < goal:
       fv = npf.fv(monthly_rate, 1, -(scaled_income - new_expenses), -fv)
       month += 1
       scaled_income = scaled_income * (1 + income_growth / 12)
    
    time_saved = original_month - month

    return({'months saved' : time_saved})


@getfired.get('/month')
async def eval_budget(income: float, assets:float, retirement_expenses: float, expenses: List[float] = Query([]), categories: List[str] = Query([]), withdraw: float = 0.04, real_rate: float = 0.06, income_growth: float = 0.05):
    monthly_rate = (1 + (real_rate)) ** (1. / 12) - 1
    fv = assets
    goal = retirement_expenses / withdraw
    incomes = []
    original_month = 0

    while fv < goal:
        incomes.append(income)
        fv = npf.fv(monthly_rate, 1, -(income - sum(expenses)), -fv)
        original_month += 1
        income = income * (1 + income_growth / 12)

    time = {}
    for cat in categories:
        new_expenses = sum(expenses) - expenses[categories.index(cat)] 
        month = 0
        incomes = []
        fv = assets
        
        while fv < goal:
           incomes.append(income)
           fv = npf.fv(monthly_rate, 1, -(income - new_expenses), -fv)
           month += 1
           income = income * (1 + income_growth / 12)

        time[cat] = original_month - month

    return({'months left' : original_month, 'categories' : time})


@getfired.get('/annual')
async def eval_budget(income: float, assets: float, curr_expenses: float, retirement_expenses: float, withdraw: float = 0.04, real_rate: float = 0.06, income_growth: float = 0.05): 
    goal = retirement_expenses / withdraw
    fv = assets
    year = 0
    incomes = []
    net_worths = []

    while fv < goal:
        incomes.append(income)
        fv = npf.fv(real_rate, 1, -(income - curr_expenses), -fv)
        net_worths.append(fv)
        year += 1
        income = income * (1 + income_growth)

    graph = np.empty((2, year))
    curr_year = date.today().year

    graph[0] = [curr_year + i for i in range(year)]
    graph[1] = net_worths

    return({'months left': year, 'graph' : graph.tolist()})


@getfired.get('/historical')
async def eval_budget(income: float, assets: float, curr_expenses: float, retirement_expenses: float, withdraw: float = 0.04, income_growth: float = 0.05):
    goal = retirement_expenses / withdraw
    start_year = 1950
    curr_year = date.today().year
    net_worths = [None] * 75
    
    for i in range(len(net_worths)):
        init = np.random.randint(start_year, curr_year - 10)
        fv = assets       
        counter = 0
        net_worths[i] = [[], []]

        while fv < 2.5 * goal and counter + init < curr_year:
            if(sp_500[init + counter] != 0):
                fv = npf.fv(sp_500[init + counter], 1, -(income * (1 + income_growth * counter) - curr_expenses), -fv)
                net_worths[i][0].append(fv)

                if(fv >= goal and not net_worths[i][1]):
                    net_worths[i][1] = counter

            counter += 1

    net_worths = [row for row in net_worths if row[1]] 
    net_worths.sort(key=lambda x: x[1])
    
    graph = [[], [], [], []]
    
    graph[3] = net_worths[3 * len(net_worths)//4 - 1]
    limit = graph[3][1]
    
    graph[0] = [curr_year + i for i in range(limit)]
    graph[1] = net_worths[len(net_worths)//4 - 1][0][:limit]
    graph[2] = net_worths[len(net_worths)//2 - 1][0][:limit]
    graph[3] = graph[3][0][:limit]
        
    lengths = [i[1] for i in net_worths]

    return({'average_years' : sum(lengths) / len(lengths), 'graph' : graph})
