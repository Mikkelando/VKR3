#!/usr/bin/env python3
from collections import defaultdict
from pathlib import Path
import os
import shutil

from matplotlib import pyplot as plt
import pyomo.environ as pyo
from pyomo.environ import value as v

from dice import START_YEAR, YEAR_STEP, TOTAL_STEPS

def get_color_alpha(scenario):
    if 'reference' in scenario:
        return 'k', 1
    if 'ssp1' in scenario:
        return 'g', 0.7
    if 'ssp2' in scenario:
        return 'gold', 0.7
    if 'ssp3' in scenario:
        return 'orange', 0.7
    if 'ssp4' in scenario:
        return 'r', 0.7
    if 'ssp5' in scenario:
        return 'm', 0.7
    return 'k', 0.2

def get_legend(scenario):
    if 'reference' in scenario:
        return 'DICE-2020'
    if 'ssp1' in scenario:
        return 'SSP1-1.9'
    if 'ssp2' in scenario:
        return 'SSP1-2.6'
    if 'ssp3' in scenario:
        return 'SSP2-4.5'
    if 'ssp4' in scenario:
        return 'SSP3-7.0'
    if 'ssp5' in scenario:
        return 'SSP5-8.5'
    return f'unknown_{scenario}'

def build_graphs(until):
    plt.rcParams.update({'font.family': 'serif'})
    filenames = ['ssp{}_solution.txt'.format(s) for s in range(1, 6)] + ['reference.txt']
    graph_path = Path(os.path.dirname(__file__)) / f'graphs{until}'
    try:
        shutil.rmtree(graph_path)
    except:
        pass
    graph_path.mkdir(parents=True, exist_ok=True)

    years = list(range(START_YEAR, until + YEAR_STEP, YEAR_STEP))

    required_graphs = [
        ('co2_emission_control', 'Carbon emission control', 'Emission control ratio'),
        ('ch4_emission_control', 'Methane emission control', 'Emission control ratio'),
        ('carbon_price', 'Carbon price', 'USD per ton of CO2'),
        ('co2_reservoir', 'Atmospheric carbon', 'GtC'),
        ('ch4_reservoir', 'Atmospheric methane', 'Tg'),
        ('land_co2_emissions', 'Natural CO2 emissions', 'GtC'),
        ('industrial_co2_emissions', 'Industrial CO2 emissions', 'GtC'),
        ('co2_emissions', 'Total CO2 emissions', 'GtC'),
        ('land_ch4_emissions', 'Natural methane emissions', 'Tg'),
        ('industrial_ch4_emissions', 'Industrial methane emissions', 'Tg'),
        ('ch4_emissions', 'Total methane emissions', 'Tg'),
        ('t_atm', 'Temperature change since 1750', '℃'),
        ('nonco2_forcings', 'Non-CO2 forcings', 'W/m²'),
        ('ch4_forcings', 'Methane forcings', 'W/m²'),
        ('co2_forcings', 'CO2 forcings', 'W/m²'),
        ('forcings', 'Total forcings', 'W/m²'),
        ('damage_frac', 'Damage fraction', 'Damage/GDP ratio'),
        ('abatement_frac', 'Abatement fraction', 'Abatement/GDP ratio'),
        ('consumption', 'Global consumption', '$ trillions'),
        ('cpc', 'Consumption per capita', '$ thousands'),
        ('capital', 'Global capital', '$ trillions'),
        ('investment', 'Global investment', '$ trillions'),
        ('saving_rate', 'Saving rate', 'Investment/GDP ratio'),
        ('gross_output', 'World GDP', '$ trillions'),
        ('growth', 'Global growth', '%'),
        ('damages', 'Damages', '$ trillions'),
        ('abatecost', 'Abatement costs', '$ trillions'),
        ('output', 'Global income', '$ trillions'),
        ('income', 'Income per capita', '$ thousands'),
        ('population', 'Global population', 'billions'),
        ('scc', 'Social cost of CO2', '$ per ton'),
        ('scch4', 'Social cost of methane', '$ per ton'),
    ]
    variables = set(var for var, _header, _ylabel in required_graphs)

    values = defaultdict(dict)
    for path in filenames:
        used_variables = set()
        with open(path) as f:
            for line in f:
                lst = line.strip().split(',')
                var, vals = lst[0], lst[1:]
                if var in variables:
                    vals = [float(val) for val in vals]
                    assert len(vals) == TOTAL_STEPS + 1, f'{var} values {len(vals)} != {TOTAL_STEPS + 1}'
                    values[var][path] = vals[:len(years)]
                    used_variables.add(var)
        is_reference = 'reference' in  path
        for var in variables:
            is_used = var in used_variables
            assert is_used or (is_reference and 'ch4' in var) or (not is_reference and var == 'population'), f"{var} is unused"

    for var, header, ylabel in required_graphs:
        graph = plt.figure()
        graph.suptitle(header, fontsize=20)
        plt.xlabel('Years', fontsize=16)
        plt.ylabel(ylabel, fontsize=16)
        for path, vals in values[var].items():
            color, alpha = get_color_alpha(path)
            label = get_legend(path)
            plt.plot(years, vals, color, alpha=alpha, label=label)
        plt.legend()
        graph.savefig(graph_path / f'{var}.png')
        plt.close()

def year(step):
    return START_YEAR + YEAR_STEP * step

def save_solution(model, status):
    pyo.assert_optimal_termination(status)
    print('\nMODEL SOLVED\n')
    with open('ssp{}_solution.txt'.format(model.ssp_scenario), 'w') as ch:
        print('(run1: eta={:.7f}; rho={:.7f})'.format(
            v(model.utility_elasticity), v(model.pure_time_preference)), file=ch)
        for var in ['saving_rate', 'co2_emission_control', 'ch4_emission_control',
            'carbon_price', 'capital', 'gross_output', 'growth',
            'land_co2_emissions', 'industrial_co2_emissions', 'co2_emissions', 'co2_reservoir',
            'land_ch4_emissions', 'industrial_ch4_emissions', 'ch4_emissions', 'ch4_reservoir',
            'ch4_forcings', 'nonco2_forcings', 'co2_forcings', 'forcings',
            't_atm', 't_ocean', 'alpha', 'cumulative_co2_emissions',
            'damage_frac', 'damages', 'abatement_frac', 'abatecost', 'output', 'income',
            'investment', 'consumption', 'cpc', 'utility']:
            print(var + ',', file=ch, end='')
            if var in ['saving_rate', 'co2_emission_control']:
                fmt = '{:.12f}'
            else:
                fmt = '{:.6f}'
            print(','.join(fmt.format(v(getattr(model, var)[year(step)])) for step in range(TOTAL_STEPS + 1)), file=ch)
        print('welfare,{:.3f}'.format(v(model.welfare)), file=ch)
        print(file=ch)
        fmt = '{:.6f}'
        print("co2_emissions_dual,", file=ch, end='')
        print(','.join(fmt.format(model.dual[model.co2_emissions_constr[year(step)]]) for step in range(TOTAL_STEPS + 1)), file=ch)
        print("ch4_emissions_dual,", file=ch, end='')
        print(','.join(fmt.format(model.dual[model.ch4_emissions_constr[year(step)]]) for step in range(TOTAL_STEPS + 1)), file=ch)
        print("consumption_dual,", file=ch, end='')
        print(','.join(fmt.format(model.dual[model.consumption_constr[year(step)]]) for step in range(TOTAL_STEPS + 1)), file=ch)
        print("scc,", file=ch, end='')
        print(','.join(fmt.format(
                -1000 * model.dual[model.co2_emissions_constr[year(step)]] /
                (0.00001 + model.dual[model.consumption_constr[year(step)]])
            ) for step in range(TOTAL_STEPS + 1)), file=ch)
        print("scch4,", file=ch, end='')
        print(','.join(fmt.format(
                -1000000 * model.dual[model.ch4_emissions_constr[year(step)]] /
                (0.00001 + model.dual[model.consumption_constr[year(step)]])
            ) for step in range(TOTAL_STEPS + 1)), file=ch)

if __name__ == '__main__':
    build_graphs(until=2100)
    build_graphs(until=2515)
    print('Graphs saved')
