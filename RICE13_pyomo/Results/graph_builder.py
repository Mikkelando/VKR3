import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Load cooperative and non-cooperative datasets
coop_df = pd.ExcelFile("coop.xlsx")
non_coop_df = pd.ExcelFile("non_coop.xlsx")

# Extract country-wise sheets (excluding global)
coop_countries = [sheet for sheet in coop_df.sheet_names if sheet != "global"]
non_coop_countries = [sheet for sheet in non_coop_df.sheet_names if sheet != "global"]

# Load data into dictionaries
coop_data = {country: coop_df.parse(country) for country in coop_countries}
non_coop_data = {country: non_coop_df.parse(country) for country in non_coop_countries}

# Extract available metrics from the first country's data
metrics = coop_data[coop_countries[0]]["Unnamed: 0"].tolist()

# Generate time points as years (starting from 2025, step of 10 years)
num_time_points = len(coop_data[coop_countries[0]].columns) - 1  # Excluding first column
time_points = np.arange(2015, 2015 + num_time_points * 10, 10)[1:]  # Start from 2025

# Create a directory to save graphs
output_dir = "graphs_new"
os.makedirs(output_dir, exist_ok=True)

# Unit mapping for axis labels (example values, adjust as needed)
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

# Creating and saving plots for each metric across all countries
for metric in metrics:
    unit_label = unit_mapping.get(metric, metric)  # Fetch unit label, default to metric name
    
    plt.figure(figsize=(12, 6))
    
    # Plot for cooperative case
    for country in coop_countries:
        metric_values = coop_data[country].set_index("Unnamed: 0").loc[metric].values[1:]  # Start from second value
        plt.plot(time_points, metric_values, label=f"{country} (Coop)", linestyle='-')

    plt.xlabel("Year")
    plt.ylabel(unit_label)
    plt.title(f"{metric}: Cooperative Case")
    plt.xticks(time_points, rotation=45)
    plt.legend()
    plt.grid(True)
    
    # Save plot
    plt.savefig(os.path.join(output_dir, f"Coop_{metric}.png"))
    plt.close()

for metric in metrics:
    unit_label = unit_mapping.get(metric, metric)  # Fetch unit label, default to metric name
    
    plt.figure(figsize=(12, 6))
    
    # Plot for non-cooperative case
    for country in non_coop_countries:
        metric_values = non_coop_data[country].set_index("Unnamed: 0").loc[metric].values[1:]  # Start from second value
        plt.plot(time_points, metric_values, label=f"{country} (Non-Coop)", linestyle='--')

    plt.xlabel("Year")
    plt.ylabel(unit_label)
    plt.title(f"{metric}: Non-Cooperative Case")
    plt.xticks(time_points, rotation=45)
    plt.legend()
    plt.grid(True)
    
    # Save plot
    plt.savefig(os.path.join(output_dir, f"Non_Coop_{metric}.png"))
    plt.close()