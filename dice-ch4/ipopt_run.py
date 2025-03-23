#!/usr/bin/env python3
import pyomo.environ as pyo
from dice import construct_model
from display import save_solution, build_graphs

for ssp_scenario in range(1, 6):
    model = construct_model(ssp_scenario)
    opt = {'max_iter': 5000}
    status = pyo.SolverFactory('ipopt').solve(model, options=opt)
    # print('\n\nCAPITAL HERE : ', model.capital.display(), '?')
    # print('\n\CH4 RESERVOIR : ', model.ch4_reservoir.display(), '?')
    # print('\n\CH4 RESERVOIR : ', ssp_scenario, model.co2_reservoir.display(), '?')
    print('\n\co2_emissions  : ', ssp_scenario, model.ch4_emissions.display(), '?')
    

    save_solution(model, status)
build_graphs(until=2100)