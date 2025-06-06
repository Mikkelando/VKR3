import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
coop_df = pd.ExcelFile("coop.xlsx")
non_coop_df = pd.ExcelFile("non_coop.xlsx")
coop_countries = [sheet for sheet in coop_df.sheet_names if sheet != "global"]
non_coop_countries = [sheet for sheet in non_coop_df.sheet_names if sheet != "global"]
coop_data = {country: coop_df.parse(country) for country in coop_countries}
non_coop_data = {country: non_coop_df.parse(country) for country in non_coop_countries}
metrics = coop_data[coop_countries[0]]["Unnamed: 0"].tolist()
num_time_points = len(coop_data[coop_countries[0]].columns) - 1 
time_points = np.arange(2015, 2015 + num_time_points * 10, 10)[1:]  
output_dir = "graphs_new"
os.makedirs(output_dir, exist_ok=True)
unit_mapping = {
    "U": "Utility (Dimensionless)",
    "K": "Capital Stock (Trillion $)",
    "S": "Saving Rate (%)",
    "I": "Investment (Trillion $)",
    "Q": "Gross Output (Trillion $)",
    "Y": "Net Output (Trillion $)",
    "C": "Consumption (Trillion $)",
    "AB": "Abatement Cost (%)",
    "D": "Damage (%)",
    "E_ind": "Industrial Emissions (GtCO₂)"
}
for metric in metrics:
    unit_label = unit_mapping.get(metric, metric)
    plt.figure(figsize=(12, 6))
    for country in coop_countries:
        metric_values = coop_data[country].set_index("Unnamed: 0").loc[metric].values[1:]  
        plt.plot(time_points, metric_values, label=f"{country} (Coop)", linestyle='-')
    plt.xlabel("Year")
    plt.ylabel(unit_label)
    plt.title(f"{metric}: Cooperative Case")
    plt.xticks(time_points, rotation=45)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f"Coop_{metric}.png"))
    plt.close()
for metric in metrics:
    unit_label = unit_mapping.get(metric, metric) 
    plt.figure(figsize=(12, 6))
    for country in non_coop_countries:
        metric_values = non_coop_data[country].set_index("Unnamed: 0").loc[metric].values[1:]  
        plt.plot(time_points, metric_values, label=f"{country} (Non-Coop)", linestyle='--')
    plt.xlabel("Year")
    plt.ylabel(unit_label)
    plt.title(f"{metric}: Non-Cooperative Case")
    plt.xticks(time_points, rotation=45)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f"Non_Coop_{metric}.png"))
    plt.close()