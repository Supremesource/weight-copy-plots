import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import seaborn as sns
import pandas as pd

def process_csv_file(file_path: str) -> List[Tuple[int, float]]:
    data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if float(row['Copier Margin']) == 0:
                window = int(row['Encryption Window'])
                gini = float(row['Gini Coefficient'])
                data.append((window, gini))
    return data

def process_all_csv_files(directory: str) -> Dict[int, List[Tuple[int, float]]]:
    subnet_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            subnet = int(filename.split('_')[-1].split('.')[0])
            subnet_data[subnet] = process_csv_file(file_path)
    return subnet_data

def smooth_data(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    df = pd.DataFrame(data)
    smoothed = df.rolling(window=window_size, min_periods=1, center=True, axis=0).mean()
    return smoothed.to_numpy()

def create_balanced_heatmap(subnet_data: Dict[int, List[Tuple[int, float]]], output_folder: str) -> None:
    all_windows = [w for data in subnet_data.values() for w, _ in data]
    max_window = max(all_windows)
    
    # Create 2D arrays to hold the Gini coefficients and data presence
    heatmap_data = np.full((max_window + 1, len(subnet_data)), np.nan)
    data_presence = np.zeros((max_window + 1, len(subnet_data)), dtype=bool)
    
    # Populate heatmap data
    for i, (subnet, data) in enumerate(sorted(subnet_data.items())):
        for window, gini in data:
            heatmap_data[window, i] = gini
            data_presence[window, i] = True
    
    # Apply light smoothing
    smoothed_data = smooth_data(heatmap_data, window_size=3)
    
    # Create the heatmap
    plt.figure(figsize=(20, 12))
    ax = sns.heatmap(smoothed_data.T, cmap='YlOrRd', cbar_kws={'label': 'Smoothed Gini Coefficient'}, 
                     mask=np.isnan(heatmap_data.T), square=False, linewidths=0,
                     xticklabels=50, yticklabels=1, vmin=0, vmax=0.5)
    
    # Overlay a hatched pattern for interpolated data
    sns.heatmap(~data_presence.T, cmap=['none'], cbar=False, alpha=0, 
                linewidths=0, xticklabels=50, yticklabels=1, ax=ax, hatch='///')
    
    plt.title('Balanced Gini Coefficient vs Encryption Window Length Across Subnets', fontsize=18)
    plt.xlabel('Encryption Window Length', fontsize=14)
    plt.ylabel('Subnets', fontsize=14)
    
    # Customize y-axis labels to show subnet numbers
    ax.set_yticklabels(sorted(subnet_data.keys()))
    
    # Add grid lines
    ax.set_axisbelow(True)
    ax.grid(color='gray', linestyle='dashed', alpha=0.5)
    
    # Add detailed description
    description = (
        "Data Processing:\n"
        "1. Raw Gini coefficients plotted against encryption window length for each subnet\n"
        "2. Light smoothing applied with a centered moving average (window size of 3)\n"
        "3. White spaces indicate no data available\n"
        "4. Hatched areas represent interpolated values\n"
        "5. Color intensity represents smoothed Gini coefficient values"
    )
    plt.text(0.5, -0.2, description, ha='center', va='center', transform=ax.transAxes, fontsize=10, wrap=True)
    
    # Add data density information
    data_points = sum(len(data) for data in subnet_data.values())
    total_cells = heatmap_data.size
    density = (data_points / total_cells) * 100
    plt.text(0.5, 1.05, f'Data Density: {density:.2f}% ({data_points} data points)', 
             ha='center', va='center', transform=ax.transAxes, fontsize=12)

    plt.tight_layout()
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "balanced_gini_window_heatmap.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Balanced heatmap analysis saved as {output_path}")

# Directory containing the CSV files
csv_directory: str = 'csv'

# Directory to save the output PNG
output_directory: str = 'examples'

# Process all CSV files
subnet_data = process_all_csv_files(csv_directory)

# Create and save the balanced heatmap analysis
create_balanced_heatmap(subnet_data, output_directory)