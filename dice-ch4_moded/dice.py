import pyomo.environ as pyo
from ssp import ssp_ch4nat, ssp_forcother

START_YEAR = 2015
YEAR_STEP = 5
SECOND_YEAR = START_YEAR + YEAR_STEP
TOTAL_STEPS = 20

# Economic constants
INITIAL_POPULATION = 7403.
POPULATION_STEP_GROWTH_RATE = 0.134
POPULATION_CAP = 11500.

INITIAL_TOTAL_FACTOR_PRODUCTIVITY = 5.115
INITIAL_TFP_GROWTH_RATE = 0.076
TFP_DECLINE_RATE = 0.005
DEPRECIATION_RATE = 0.1
CAPITAL_ELASTICITY = 0.3

MINIMAL_CAPITAL_TRILLIONS_USD = 1
INITIAL_CAPITAL_TRILLIONS_USD = 223
MINIMAL_CONSUMPTION_PER_CAPITA_USD = 100

INITIAL_LAND_CO2_EMISSIONS = 2.6
INITIAL_INDUSTRIAL_CO2_EMISSIONS = 35.85
INITIAL_INDUSTRIAL_CH4_EMISSIONS = 363
INITIAL_EMISSION_CONTROL = 0.03
INITIAL_GDP = 105.5
INITIAL_CO2_INTENSITY = INITIAL_INDUSTRIAL_CO2_EMISSIONS / (INITIAL_GDP * (1 - INITIAL_EMISSION_CONTROL))
INITIAL_CH4_INTENSITY = INITIAL_INDUSTRIAL_CH4_EMISSIONS / (INITIAL_GDP * (1 - INITIAL_EMISSION_CONTROL))
C_INTENSITY_GROWTH = [-0.0152]
while len(C_INTENSITY_GROWTH) < TOTAL_STEPS + 1:
    C_INTENSITY_GROWTH.append(C_INTENSITY_GROWTH[-1] * 0.999 ** YEAR_STEP)
LAND_CO2_EMISSIONS_DECAY = 1 - 0.115

THETA = 2.6
INITIAL_BACKSTOP = 550
BACKSTOP_DECAY = 1 - 0.025

PSI = 0.007438

# Climate constants
ACCUMULATION_COEFF = YEAR_STEP / 3.666
INITIAL_CUMULATIVE_CO2_EMISSIONS_GTC = 597 # 400+197, where Ecum[0] is 400 and CumLand[0] == 197 in AMPL code
EQUILIBRIUM_CONCENTRATION_GTC = 588
METHANE_EQUILIBRIUM_PPB_SQRT = 772 ** 0.5

BOXES = 4
INITIAL_C_CYCLE_GTC = [127.159, 93.313, 37.840, 7.721]
INITIAL_TGCH4 = 5089
assert len(INITIAL_C_CYCLE_GTC) == BOXES
T_SCALE = [1000000, 394.4, 36.54, 4.304]
assert len(T_SCALE) == BOXES
FRACTION = [0.217, 0.224, 0.282, 0.276]
assert len(FRACTION) == BOXES

KAPPA = 3.6813 # Forcings of equilibrium CO2 doubling (Wm-2)
METHANE_YEARLY_ATM_DECAY = 0.9

# change in Celsius degrees since 1900, adjusted to only include antropogenic forcing
INITIAL_ATMOSPHERIC_TEMPERATURE = 1.243
MAX_TEMPERATURE_LIMIT = 5.113
INITIAL_OCEAN_TEMPERATURE = 0.324
XI1, XI2, XI3, XI4 = 7.3, KAPPA / 3.1, 0.73, 106

def add_climate(model):
    # special climatic coefficient constrained by alpha_calibration in the end
    model.alpha = pyo.Var(model.years, bounds=(0.01, 100))

    model.c_cycle = pyo.Var(model.years, range(BOXES))
    for box in range(BOXES):
        model.c_cycle[START_YEAR, box].fix(INITIAL_C_CYCLE_GTC[box])
    def c_cycle_rule(model, year, box):
        if year == START_YEAR:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        scale = model.alpha[prev] * T_SCALE[box]
        emissions_coeff = FRACTION[box] * ACCUMULATION_COEFF / YEAR_STEP * \
            sum(pyo.exp(-(YEAR_STEP - y) / scale) for y in range(YEAR_STEP))
        return model.c_cycle[year, box] == model.co2_emissions[prev] * emissions_coeff +\
            model.c_cycle[prev, box] * pyo.exp(-YEAR_STEP / scale)
    model.c_cycle_dynamics = pyo.Constraint(model.years, range(BOXES), rule=c_cycle_rule)

    def co2_reservoir_rule(model, year):
        return sum(model.c_cycle[year, box] for box in range(BOXES)) + EQUILIBRIUM_CONCENTRATION_GTC
    model.co2_reservoir = pyo.Expression(model.years, rule=co2_reservoir_rule)

    model.ch4_reservoir = pyo.Var(model.years, bounds=(1, None))
    model.ch4_reservoir[START_YEAR].fix(INITIAL_TGCH4)
    def ch4_reservoir_rule(model, year):
        if year == START_YEAR:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        reservoir = model.ch4_reservoir[prev]
        for _ in range(YEAR_STEP):
            reservoir = (reservoir + model.ch4_emissions[prev]) * METHANE_YEARLY_ATM_DECAY
        return model.ch4_reservoir[year] == reservoir
    model.ch4_dynamics = pyo.Constraint(model.years, rule=ch4_reservoir_rule)
    

    def methane_forcings_rule(model, year):
        return 0.036 * (pyo.sqrt(model.ch4_reservoir[year] / 2.75) - METHANE_EQUILIBRIUM_PPB_SQRT)
    model.ch4_forcings = pyo.Expression(model.years, rule=methane_forcings_rule)

    def nonco2_forcings_rule(model, year):
        return model.ch4_forcings[year] + ssp_forcother(model.ssp_scenario, year)
    model.nonco2_forcings = pyo.Expression(model.years, rule=nonco2_forcings_rule)

    def co2_forcings_rule(model, year):
        return KAPPA * pyo.log(model.co2_reservoir[year] / EQUILIBRIUM_CONCENTRATION_GTC) / pyo.log(2)
    model.co2_forcings = pyo.Expression(model.years, rule=co2_forcings_rule)

    def forcings_rule(model, year):
        return model.co2_forcings[year] + model.nonco2_forcings[year]
    model.forcings = pyo.Expression(model.years, rule=forcings_rule)

    model.t_atm = pyo.Var(model.years, bounds=(0, MAX_TEMPERATURE_LIMIT))
    model.t_atm_short = pyo.Var(model.years, range(YEAR_STEP + 1), bounds=(0, MAX_TEMPERATURE_LIMIT))
    model.t_ocean = pyo.Var(model.years, bounds=(-1, 20))
    model.t_atm[START_YEAR].fix(INITIAL_ATMOSPHERIC_TEMPERATURE)
    model.t_ocean[START_YEAR].fix(INITIAL_OCEAN_TEMPERATURE)
    def t_atm_rule(model, year, step):
        if step == 0:
            return model.t_atm_short[year, 0] == model.t_atm[year]
        if year == START_YEAR:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        if step == YEAR_STEP + 1:
            return model.t_atm_short[prev, YEAR_STEP] == model.t_atm[year]
        prev_val = model.t_atm_short[prev, step - 1]
        return model.t_atm_short[prev, step] == prev_val + 1 / XI1 * \
            ((model.forcings[year] - XI2 * prev_val)- (prev_val - model.t_ocean[prev]) * XI3)
    model.t_atm_law = pyo.Constraint(model.years, range(YEAR_STEP + 2), rule=t_atm_rule)
    def t_ocean_rule(model, year):
        if year == START_YEAR:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        return model.t_ocean[year] == model.t_ocean[prev] + YEAR_STEP * XI3 / XI4 *\
            (model.t_atm[prev] - model.t_ocean[prev])
    model.t_ocean_law = pyo.Constraint(model.years, rule=t_ocean_rule)

    # upper bound by available fossil fuels
    model.cumulative_co2_emissions = pyo.Var(model.years)
    model.cumulative_co2_emissions[START_YEAR].fix(INITIAL_CUMULATIVE_CO2_EMISSIONS_GTC)
    def co2_emissions_accum_rule(model, year):
        if year == START_YEAR:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        return model.cumulative_co2_emissions[year] == model.cumulative_co2_emissions[prev] +\
            ACCUMULATION_COEFF * model.co2_emissions[prev]
    model.co2_emissions_accumulation = pyo.Constraint(model.years, rule=co2_emissions_accum_rule)

    def alpha_rule(model, year):
        scale = [model.alpha[year] * T_SCALE[box] for box in range(BOXES)]
        return 35 + 0.019 * (model.cumulative_co2_emissions[year] - (model.co2_reservoir[year] - EQUILIBRIUM_CONCENTRATION_GTC))\
            + 4.165 * model.t_atm[year] == sum(
                scale[box] * FRACTION[box] * (1 - pyo.exp(-100 / scale[box]))
                for box in range(BOXES))
    model.alpha_calibration = pyo.Constraint(model.years, rule=alpha_rule)

def construct_model(ssp_scenario):
    model = pyo.ConcreteModel()
    model.ssp_scenario = ssp_scenario
    model.years = pyo.RangeSet(START_YEAR, START_YEAR + YEAR_STEP * TOTAL_STEPS, YEAR_STEP)
    assert len(model.years) == TOTAL_STEPS + 1

    model.utility_elasticity = pyo.Param(initialize=1.0000001, mutable=True)
    model.pure_time_preference = pyo.Param(initialize=0.005, mutable=True)

    def discount_rule(model, year):
        return 1. / ((1. + model.pure_time_preference) ** (year - START_YEAR))
    model.discount_factor = pyo.Expression(model.years, rule=discount_rule)

    # These are our two policy decisions
    model.co2_emission_control = pyo.Var(model.years, bounds=(0, 1.2))
    model.saving_rate = pyo.Var(model.years, bounds=(0, 1))

    def ch4_control_rule(model, year):
        coeff = 0.314 # such that model.ch4_emission_control is 1 when co2_emission_control is 1.2
        return (1 - pyo.exp(-coeff * model.co2_emission_control[year])) / coeff
    model.ch4_emission_control = pyo.Expression(model.years, rule=ch4_control_rule)

    model.co2_emission_control[START_YEAR].fix(INITIAL_EMISSION_CONTROL)
    def negative_emissions_rule(model, year):
        if year >= 2050:
            return pyo.Constraint.Skip
        return model.co2_emission_control[year] <= 1
    model.negative_emissions_tech = pyo.Constraint(model.years, rule=negative_emissions_rule)
    def ectrl_change_rule(model, year):
        if year < 2050:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        return model.co2_emission_control[year] <= model.co2_emission_control[prev] * 1.1
    model.ectrl_change = pyo.Constraint(model.years, rule=ectrl_change_rule)

    def population_rule(model, year):
        if year == START_YEAR:
            return INITIAL_POPULATION
        previous = model.population[year - YEAR_STEP]
        return previous * ((POPULATION_CAP / previous) ** POPULATION_STEP_GROWTH_RATE)
    model.population = pyo.Param(model.years, initialize=population_rule)

    def total_factor_productivity_rule(model, year):
        if year == START_YEAR:
            return INITIAL_TOTAL_FACTOR_PRODUCTIVITY
        prev = year - YEAR_STEP
        prev_tfp_growth_rate = INITIAL_TFP_GROWTH_RATE * \
            pyo.exp(-TFP_DECLINE_RATE * (prev - START_YEAR))
        return model.tfp[prev] / (1. - prev_tfp_growth_rate)
    model.tfp = pyo.Param(model.years, initialize=total_factor_productivity_rule)

    model.capital = pyo.Var(model.years, bounds=(MINIMAL_CAPITAL_TRILLIONS_USD, None))
    model.capital[START_YEAR].fix(INITIAL_CAPITAL_TRILLIONS_USD)


    def cobb_douglas_rule(model, year):
        labour_elasticity = 1. - CAPITAL_ELASTICITY
        return model.tfp[year] *\
            ((model.population[year] / 1000) ** labour_elasticity) *\
                (model.capital[year] ** CAPITAL_ELASTICITY)
    model.gross_output = pyo.Expression(model.years, rule=cobb_douglas_rule)

    def growth_rule(model, year):
        if year == START_YEAR:
            return 0
        return (model.gross_output[year] / model.gross_output[year - YEAR_STEP] - 1) * 100 / YEAR_STEP
    model.growth = pyo.Expression(model.years, rule=growth_rule)

    def co2_intensity_rule(model, year):
        if year == START_YEAR:
            return INITIAL_CO2_INTENSITY
        prev = year - YEAR_STEP
        return model.co2_intensity[prev] * pyo.exp(
            C_INTENSITY_GROWTH[(prev - START_YEAR) // YEAR_STEP] * YEAR_STEP)
    model.co2_intensity = pyo.Param(model.years, rule=co2_intensity_rule)

    def ch4_intensity_rule(model, year):
        if year == START_YEAR:
            return INITIAL_CH4_INTENSITY
        prev = year - YEAR_STEP
        return model.ch4_intensity[prev] * pyo.exp(
            C_INTENSITY_GROWTH[(prev - START_YEAR) // YEAR_STEP] * YEAR_STEP)
    model.ch4_intensity = pyo.Param(model.years, rule=ch4_intensity_rule)

    def land_co2_rule(model, year):
        if year == START_YEAR:
            return INITIAL_LAND_CO2_EMISSIONS
        prev = year - YEAR_STEP
        return model.land_co2_emissions[prev] * LAND_CO2_EMISSIONS_DECAY
    model.land_co2_emissions = pyo.Param(model.years, rule=land_co2_rule)

    def land_ch4_rule(model, year):
        return ssp_ch4nat(model.ssp_scenario, year)
    model.land_ch4_emissions = pyo.Param(model.years, rule=land_ch4_rule)

    def eind_co2_rule(model, year):
        return (1 - model.co2_emission_control[year]) * model.co2_intensity[year] *\
            model.gross_output[year]
    model.industrial_co2_emissions = pyo.Expression(model.years, rule=eind_co2_rule)

    def eind_ch4_rule(model, year):
        return (1 - model.ch4_emission_control[year]) * model.ch4_intensity[year] *\
            model.gross_output[year]
    model.industrial_ch4_emissions = pyo.Expression(model.years, rule=eind_ch4_rule)

    model.co2_emissions = pyo.Var(model.years)
    def co2_emissions_rule(model, year):
        return model.co2_emissions[year] == model.land_co2_emissions[year] + model.industrial_co2_emissions[year]
    model.co2_emissions_constr = pyo.Constraint(model.years, rule=co2_emissions_rule)

    model.ch4_emissions = pyo.Var(model.years)
    def ch4_emissions_rule(model, year):
        return model.ch4_emissions[year] == model.land_ch4_emissions[year] + model.industrial_ch4_emissions[year]
    model.ch4_emissions_constr = pyo.Constraint(model.years, rule=ch4_emissions_rule)

    model.second_year_ectrl = pyo.Constraint(expr=(model.co2_emission_control[SECOND_YEAR] ==
        1 - (INITIAL_INDUSTRIAL_CO2_EMISSIONS * 1.01 ** YEAR_STEP) /
            (model.co2_intensity[SECOND_YEAR] * model.gross_output[SECOND_YEAR])))
    def extra_ectrl_rule(model, year):
        if year >= 2050 or year <= SECOND_YEAR:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        return model.co2_emission_control[year] <= 1 - (model.industrial_co2_emissions[prev] - 10) /\
            (model.co2_intensity[year] * model.gross_output[year])
    model.extra_ectrl_constraint = pyo.Constraint(model.years, rule=extra_ectrl_rule)

    add_climate(model)

    def damage_rule(model, year):
        return PSI * (model.t_atm[year] - 0.115) ** 2
    model.damage_frac = pyo.Expression(model.years, rule=damage_rule)

    def backstop_rule(model, year):
        if year == START_YEAR:
            return INITIAL_BACKSTOP
        prev = year - YEAR_STEP
        return model.backstop[prev] * BACKSTOP_DECAY
    model.backstop = pyo.Param(model.years, initialize=backstop_rule)

    def carbon_price_rule(model, year):
        return model.backstop[year] * model.co2_emission_control[year] ** (THETA - 1)
    model.carbon_price = pyo.Expression(model.years, rule=carbon_price_rule)

    def abatement_rule(model, year):
        return model.backstop[year] * model.co2_intensity[year] / 1000 / THETA *\
            model.co2_emission_control[year] ** THETA
    model.abatement_frac = pyo.Expression(model.years, rule=abatement_rule)

    def abatecost_rule(model, year):
        return model.abatement_frac[year] * model.gross_output[year]
    model.abatecost = pyo.Expression(model.years, rule=abatecost_rule)

    def damages_rule(model, year):
        return model.damage_frac[year] * model.gross_output[year]
    model.damages = pyo.Expression(model.years, rule=damages_rule)

    def output_rule(model, year):
        return model.gross_output[year] * (1 - model.damage_frac[year] - model.abatement_frac[year])
    model.output = pyo.Expression(model.years, rule=output_rule)

    def income_rule(model, year):
        return model.output[year] / model.population[year] * 1000
    model.income = pyo.Expression(model.years, rule=income_rule)

    def investment_rule(model, year):
        return model.output[year] * model.saving_rate[year]
    model.investment = pyo.Expression(model.years, rule=investment_rule)

    model.consumption = pyo.Var(model.years, bounds=(0, None))
    def consumption_rule(model, year):
        return model.consumption[year] == model.output[year] * (1 - model.saving_rate[year])
    model.consumption_constr = pyo.Constraint(model.years, rule=consumption_rule)

    def capital_rule(model, year):
        if year == START_YEAR:
            return pyo.Constraint.Skip
        prev = year - YEAR_STEP
        return model.capital[year] == YEAR_STEP * model.investment[prev] +\
            (1. - DEPRECIATION_RATE) ** YEAR_STEP * model.capital[prev]
    # print("BEFORE: ", model.capital.display())
    model.capital_dynamics = pyo.Constraint(model.years, rule=capital_rule)
    # print("AFTER: ", model.capital.display())

    model.cpc = pyo.Var(model.years, bounds=(MINIMAL_CONSUMPTION_PER_CAPITA_USD / 1000, None))

    def cpc_rule(model, year):
        return model.consumption[year] == model.cpc[year] * model.population[year] / 1000
    model.cpc_law = pyo.Constraint(model.years, rule=cpc_rule)

    def utility_rule(model, year):
        u = 1 - model.utility_elasticity
        return model.cpc[year] ** u / u
    model.utility = pyo.Expression(model.years, rule=utility_rule)
    model.welfare = pyo.Objective(sense=pyo.maximize,
        expr=pyo.sum_product(model.population, model.utility, model.discount_factor))

    model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    print('MODEL CONSTRUCTED')
   
    return model
