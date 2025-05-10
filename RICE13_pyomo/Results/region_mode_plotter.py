import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse

# Словарь единиц измерения
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

def plot_comparison(region_code: str, variable: str,
                    coop_path='coop.xlsx', non_coop_path='non_coop.xlsx',
                    output_dir='output'):
    # Загрузка данных
    coop_data = pd.read_excel(coop_path, sheet_name=None, index_col=0)
    non_coop_data = pd.read_excel(non_coop_path, sheet_name=None, index_col=0)
    
    # Проверка
    if region_code not in coop_data or region_code not in non_coop_data:
        raise ValueError(f"Регион '{region_code}' отсутствует в файлах.")
    if variable not in coop_data[region_code].index or variable not in non_coop_data[region_code].index:
        raise ValueError(f"Переменная '{variable}' отсутствует у региона '{region_code}'.")

    # Получение временных рядов
    coop_series = coop_data[region_code].loc[variable]
    non_coop_series = non_coop_data[region_code].loc[variable]
    years = [2015 + 10 * i for i in range(len(coop_series))]

    # Название оси Y
    y_label = unit_mapping.get(variable, variable)

    # Создание папки
    folder = os.path.join(output_dir, region_code)
    os.makedirs(folder, exist_ok=True)

    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(years, coop_series, label='Cooperative', linewidth=2)
    plt.plot(years, non_coop_series, label='Non-Cooperative', linewidth=2, linestyle='--')
    plt.title(f"{variable} — {region_code}")
    plt.xlabel("Year")
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)

    # Сохранение
    filepath = os.path.join(folder, f"{variable}.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    print(f"График сохранён в: {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сравнение показателей в кооп/некооп режимах модели RICE2025-CH4")
    parser.add_argument("--region", required=True, help="Код региона (например, US, CHI, EU)")
    parser.add_argument("--var", required=True, help="Название переменной (например, Y, C, T_at)")
    parser.add_argument("--coop", default="coop.xlsx", help="Файл кооперативного режима")
    parser.add_argument("--noncoop", default="non_coop.xlsx", help="Файл некооперативного режима")
    parser.add_argument("--out", default="region_mode_compare", help="Папка для сохранения")

    args = parser.parse_args()
    plot_comparison(args.region, args.var, args.coop, args.noncoop, args.out)