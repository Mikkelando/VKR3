import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ===== Настройки стиля и легенд =====
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
        return 'SSP1'
    if 'ssp2' in scenario:
        return 'SSP2'
    if 'ssp3' in scenario:
        return 'SSP3'
    if 'ssp4' in scenario:
        return 'SSP4'
    if 'ssp5' in scenario:
        return 'SSP5'
    # if 'RICE2025-CH4' in scenario:
    #     return 'RICE2025-CH4'
    return f'unknown_{scenario}'

# ===== Функция построения графика =====
def plot_scc_or_scch4(data_dict, years, var_name, save_path):
    plt.rcParams.update({'font.family': 'serif'})
    plt.figure(figsize=(10, 6))

    title = 'Social cost of CO2' if var_name == 'scc' else 'Social cost of methane'
    ylabel = '$ per ton'
    plt.title(title, fontsize=20)
    plt.xlabel('Years', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)

    for scenario, values in data_dict.items():
        color, alpha = get_color_alpha(scenario)
        base_scenario = get_legend(scenario)
        label = base_scenario + (' (noncoop)' if 'non' in scenario else ' (coop)')
        plt.plot(years[:len(values)], values, label=label, color=color, alpha=alpha)

    plt.legend()
    plt.grid(True)
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path)
    plt.close()

# ===== Основной блок =====
def main():
    base_dir = Path("ssp_results")
    ssp_list = ['ssp1', 'ssp2', 'ssp3', 'ssp4', 'ssp5']
    file_types = ['scc_coop', 'scc_noncoop', 'scch4_coop', 'scch4_noncoop']

    scc_data = {}
    scch4_data = {}

    for ssp in ssp_list:
        for file_type in file_types:
            file_path = base_dir / ssp / f"{file_type}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path, header=None, sep=';')
                if df.shape[0] > 1:
                    scenario_key = f"{ssp}_{file_type}"
                    # values = df.iloc[1, :].astype(float).values


                    row = df.iloc[1, :].dropna().values[0]

                    
                    values = [float(x) for x in row.split(',')]
                    if not "scch4" in file_type:
                        scc_data[scenario_key] = values
                    elif "scch4" in file_type:
                        scch4_data[scenario_key] = [x/1000 for x in values] 

    years = [2025 + i * 10 for i in range(14)]  

    # print(scc_data)
    # print(scch4_data)
    plot_scc_or_scch4(scc_data, years, 'scc', 'post_work/scc_all.png')
    plot_scc_or_scch4(scch4_data, years, 'scch4', 'post_work/scch4_all.png')
    print("✅ Графики сохранены в папку ")

if __name__ == "__main__":
    main()