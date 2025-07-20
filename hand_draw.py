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
    return f'unknown_{scenario}'

# ===== Глобальные графики =====
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

# ===== Графики по регионам =====
def plot_regions(data_dict, years, var_name, save_path_dir):
    plt.rcParams.update({'font.family': 'serif'})
    regions = list(next(iter(data_dict.values())).keys())

    for region in regions:
        plt.figure(figsize=(10, 6))
        title = f"{'SCC' if var_name == 'scc' else 'SCCH4'} — {region}"
        plt.title(title, fontsize=20)
        plt.xlabel('Years', fontsize=16)
        plt.ylabel('$ per ton', fontsize=16)

        for scenario, region_dict in data_dict.items():
            if region not in region_dict:
                continue
            color, alpha = get_color_alpha(scenario)
            base_scenario = get_legend(scenario)
            label = base_scenario + (' (noncoop)' if 'non' in scenario else ' (coop)')
            values = region_dict[region]
            plt.plot(years[:len(values)], values, label=label, color=color, alpha=alpha)

        plt.legend()
        plt.grid(True)
        Path(save_path_dir).mkdir(parents=True, exist_ok=True)
        plt.savefig(Path(save_path_dir) / f'{var_name}_{region}.png')
        plt.close()

# ===== Загрузка агрегированных SCC и SCCH4 =====
def process_aggregated_data():
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
                    row = df.iloc[1, :].dropna().values[0]
                    values = [float(x) for x in row.split(',')]
                    if "scch4" in file_type:
                        scch4_data[scenario_key] = [x / 1000 for x in values]
                    else:
                        scc_data[scenario_key] = values

    return scc_data, scch4_data

# ===== Загрузка региональных данных =====
def process_region_files():
    base_dir = Path("ssp_results")
    ssp_list = ['ssp1', 'ssp2', 'ssp3', 'ssp4', 'ssp5']
    suffixes = ['scc_coop_regions.csv', 'scc_noncoop_regions.csv',
                'scch4_coop_regions.csv', 'scch4_noncoop_regions.csv']

    region_data_scc = {}
    region_data_scch4 = {}

    for ssp in ssp_list:
        for suffix in suffixes:
            file_path = base_dir / ssp / suffix
            if file_path.exists():
                df = pd.read_csv(file_path, header=None)
                region_dict = {}
                for i in range(1, df.shape[0]):
                    region = df.iloc[i, 0]
                    raw_values = df.iloc[i, 1:].dropna().values
                    parsed = [float(x) for x in ','.join(map(str, raw_values)).split(',')]
                    if 'scch4' in suffix:
                        parsed = [x / 1000 for x in parsed]
                    region_dict[region] = parsed
                scenario_key = f"{ssp}_{suffix.split('.')[0]}"
                if 'scch4' in suffix:
                    region_data_scch4[scenario_key] = region_dict
                else:
                    region_data_scc[scenario_key] = region_dict

    return region_data_scc, region_data_scch4

# ===== Основной блок =====
def main():
    years = [2025 + i * 10 for i in range(14)]

    # Глобальные значения SCC/SCCH4
    scc_data, scch4_data = process_aggregated_data()
    plot_scc_or_scch4(scc_data, years, 'scc', 'post_work/scc_all.png')
    plot_scc_or_scch4(scch4_data, years, 'scch4', 'post_work/scch4_all.png')

    # Региональные значения
    region_data_scc, region_data_scch4 = process_region_files()
    plot_regions(region_data_scc, years, 'scc', 'post_work/regions/scc')
    plot_regions(region_data_scch4, years, 'scch4', 'post_work/regions/scch4')

    print("✅ Все графики успешно сохранены в папку 'post_work/'")

if __name__ == "__main__":
    main()