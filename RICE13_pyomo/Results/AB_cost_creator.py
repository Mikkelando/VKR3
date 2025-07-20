import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse


unit_mapping = {
    "U": "Utility (Dimensionless)",
    "K": "Capital Stock (Trillion $)",
    "S": "Saving Rate (%)",
    "I": "Investment (Trillion $)",
    "Q": "Gross Output (Trillion $)",
    "Y": "Net Output (Trillion $)",
    "C": "Consumption (Trillion $)",
    "AB": "Abatement Cost (Trillion $)",
    "D": "Damage (Trillion $)",
    "E_ind": "Industrial CO₂ Emissions (GtCO₂)",
    "E_CH4_ind": "Industrial CH₄ Emissions (MtCH₄)",
    "mu": "μ - Emission Control (CO₂)",
    "mu_CH4": "μ - Emission Control (CH₄)",
    "T_at": "Atmospheric Temperature (°C)",
    "T_lo": "Lower Ocean Temperature (°C)",
    "F": "Radiative Forcing (W/m²)",
    "M_at": "Atmospheric CO₂ (GtC)",
    "M_CH4_at": "Atmospheric CH₄ (MtCH₄)",
}

def plot_comparison(region_code: str,
                    coop_path='coop.xlsx', non_coop_path='non_coop.xlsx',
                    output_dir='output'):
    # Загрузка данных
    coop_data = pd.read_excel(coop_path, sheet_name=None, index_col=0)
    non_coop_data = pd.read_excel(non_coop_path, sheet_name=None, index_col=0)

    # Проверка
    if region_code not in coop_data or region_code not in non_coop_data:
        raise ValueError(f"Регион '{region_code}' отсутствует в файлах.")


    # Получение временных рядов
    coop_series_D = coop_data[region_code].loc['AB']
    coop_series_Q = coop_data[region_code].loc['Q']

    non_coop_series_D = non_coop_data[region_code].loc['AB']
    non_coop_series_Q = non_coop_data[region_code].loc['Q']

    # print(coop_series_D)

    # new_coop_data = [( coop_series_D[i]/ (1 + (coop_series_D[i])**10) ) * coop_series_Q[i] for i in range(len(coop_series_D))]

    # new_noncoop_data = [( non_coop_series_D[i]/ (1 + (non_coop_series_D[i])**10) ) * non_coop_series_Q[i] for i in range(len(non_coop_series_D))]

    new_coop_data = [ coop_series_D.iloc[i] * coop_series_Q.iloc[i]  for i in range(len(coop_series_D))]
    new_noncoop_data = [ non_coop_series_D.iloc[i] * non_coop_series_Q.iloc[i] for i in range(len(non_coop_series_D))]


    years = [2015 + 10 * i for i in range(len(new_coop_data))]

    # Ограничение по годам: только 2025–2100
    min_year, max_year = 2025, 2100
    filtered = [(y, c, n) for y, c, n in zip(years, new_coop_data, new_noncoop_data)
                if min_year <= y <= max_year]

    if not filtered:
        print(f"⚠️ Нет данных в диапазоне {min_year}–{max_year} для переменной региона '{region_code}'.")
        return

    years, coop_series, non_coop_series = zip(*filtered)

    # Название оси Y
    y_label = unit_mapping.get('AB Cost (Trillion $)', 'AB Cost (Trillion $)')

    # Создание папки
    folder = os.path.join(output_dir, region_code)
    os.makedirs(folder, exist_ok=True)

    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(years, coop_series, label='Cooperative', linewidth=2)
    plt.plot(years, non_coop_series, label='Non-Cooperative', linewidth=2, linestyle='--')
    plt.title(f"AB Cost — {region_code}")
    plt.xlabel("Year")
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)

    # Сохранение
    filepath = os.path.join(folder, f"AB_cost.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    print(f"✅ График сохранён в: {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сравнение показателей в кооп/некооп режимах модели RICE2025-CH4")
    parser.add_argument("--region", required=True, help="Код региона (например, US, CHI, EU)")

    parser.add_argument("--coop", default="coop.xlsx", help="Файл кооперативного режима")
    parser.add_argument("--noncoop", default="non_coop.xlsx", help="Файл некооперативного режима")
    parser.add_argument("--out", default="AB_cost", help="Папка для сохранения")

    args = parser.parse_args()
    plot_comparison(args.region, args.coop, args.noncoop, args.out)
