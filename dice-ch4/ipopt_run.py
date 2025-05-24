#!/usr/bin/env python3
import pyomo.environ as pyo
from dice import construct_model
from display import save_solution, build_graphs

for ssp_scenario in range(1, 6):
    model = construct_model(ssp_scenario)
    opt = {'max_iter': 5000}
    status = pyo.SolverFactory('ipopt').solve(model, options=opt)
    save_solution(model, status)
build_graphs(until=2100)