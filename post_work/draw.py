from matplotlib import pyplot as plt
from pathlib import Path

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
    if 'RICE2025-CH4' in scenario:
        return 'orange', 1
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
    if 'RICE2025-CH4' in scenario:
        return 'RICE2025-CH4'
    return f'unknown_{scenario}'

# Названия графиков и подписей по переменным
VAR_LABELS = {
    'mu': ('Carbon emission control', 'Emission control ratio'),
    'mu_CH4': ('Methane emission control', 'Emission control ratio'),
    'carbon_price': ('Carbon price', 'USD per ton of CO2'),
    'M_at': ('Atmospheric carbon', 'GtC'),
    'M_CH4_at': ('Atmospheric methane', 'Tg'),
    'land_co2_emissions': ('Natural CO2 emissions', 'GtC'),
    'E_ind': ('Industrial CO2 emissions', 'GtC'),
    'E_tot': ('Total CO2 emissions', 'GtC'),
    'land_ch4_emissions': ('Natural methane emissions', 'Tg'),
    'E_CH4_ind': ('Industrial methane emissions', 'Tg'),
    'E_CH4_tot': ('Total methane emissions', 'Tg'),
    'T_at': ('Temperature change since 1750', '℃'),
    'nonco2_forcings': ('Non-CO2 forcings', 'W/m²'),
    'ch4_forcings': ('Methane forcings', 'W/m²'),
    'co2_forcings': ('CO2 forcings', 'W/m²'),
    'F': ('Total forcings', 'W/m²'),
    'D': ('Damage fraction', 'Damage/GDP ratio'),
    'AB': ('Abatement fraction', 'Abatement/GDP ratio'),
    'C': ('Global consumption', '$ trillions'),
    'cpc': ('Consumption per capita', '$ thousands'),
    'K': ('Global capital', '$ trillions'),
    'I': ('Global investment', '$ trillions'),
    'S': ('Saving rate', 'Investment/GDP ratio'),
    'Q': ('World GDP', '$ trillions'),
    'growth': ('Global growth', '%'),
    'D_cost': ('Damages', '$ trillions'),
    'AB_cost': ('Abatement costs', '$ trillions'),
    'Y': ('Global income', '$ trillions'),
    'income': ('Income per capita', '$ thousands'),
    'population': ('Global population', 'billions'),
    'scc': ('Social cost of CO2', '$ per ton'),
    'scch4': ('Social cost of methane', '$ per ton'),
}

def plot_variable_graph(var_name, values, years, scenario_name, save_path):
    title, ylabel = VAR_LABELS.get(var_name, (var_name, ''))
    color, alpha = get_color_alpha(scenario_name)
    label = get_legend(scenario_name)

    plt.rcParams.update({'font.family': 'serif'})
    fig = plt.figure()
    fig.suptitle(title, fontsize=20)
    plt.xlabel('Years', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.plot(years, values, color=color, alpha=alpha, label=label)
    plt.legend()

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path)
    plt.close()



import pandas as pd
from pathlib import Path

def process_excel_and_plot(filepath, sheet_name, years_start,years_end, save_dir, scenario_name):
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

    # Считаем, что:
    # - переменные в строках начиная с 2-й (индекс 1)
    # - годы по колонкам начиная с B (индекс 1)
    variable_names = df.iloc[1:, 0].values  # первая колонка
    data = df.iloc[1:, 1:].values  # остальные данные

    # Кол-во лет = кол-во столбцов
    num_years = data.shape[1]
    years = [years_start + 10 * i for i in range(num_years)]
    years = [y for y in years if y <= years_end]
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # Преобразование и построение графиков
    for i, var in enumerate(variable_names):
        var_data = data[i, :].astype(float)
        plot_variable_graph(
            var_name=str(var),
            values=var_data[:len(years)],
            years=years,
            scenario_name=scenario_name,
            save_path=Path(save_dir) / f"{var}_{scenario_name}.png"
        )


if __name__ == "__main__":
    process_excel_and_plot(
        filepath="coop.xlsx",        
        sheet_name="ES",             
        years_start=2025,            
        years_end = 2105,
        save_dir="plots_ES_coop",            
        scenario_name="RICE2025-CH4"         
    )
    process_excel_and_plot(
        filepath="non_coop.xlsx",        
        sheet_name="ES",             
        years_start=2025,           
        years_end = 2105,
        save_dir="plots_ES_noncoop",            
        scenario_name="RICE2025-CH4"         
    )
    