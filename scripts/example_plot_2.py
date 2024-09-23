import os
import csv
from collections import defaultdict
import statistics
import plotly.graph_objects as go
import seaborn as sns
from typing import DefaultDict
import plotly.express as px
import matplotlib.pyplot as plt
import math
import pandas as pd
import matplotlib.colors as mcolors
import colorsys


def process_csv_file(file_path: str) -> DefaultDict[float, list[float]]:
    data: DefaultDict[float, list[float]] = defaultdict(list)
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            p: float = float(row['Copier Margin'])
            age: float = float(row['Black Box Age'])
            data[p].append(age)
    return data


def process_all_csv_files(directory: str) -> dict[int, DefaultDict[float, list[float]]]:
    subnet_data: dict[int, DefaultDict[float, list[float]]] = {}
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path: str = os.path.join(directory, filename)
            subnet: int = int(filename.split('_')[-1].split('.')[0])
            subnet_data[subnet] = process_csv_file(file_path)
    return subnet_data


def calculate_average_ages(subnet_data: dict[int, DefaultDict[float, list[float]]]) -> dict[int, dict[float, float]]:
    avg_data: dict[int, dict[float, float]] = {}
    for subnet, data in subnet_data.items():
        avg_data[subnet] = {p: statistics.mean(
            ages) for p, ages in data.items()}
    return avg_data

def create_plot(avg_data: dict[int, dict[float, float]], output_folder: str) -> None:
    # Convert the data to a format suitable for Seaborn
    plot_data = []
    for subnet, data in avg_data.items():
        for p, age in data.items():
            plot_data.append({'Subnet': f'Subnet {subnet}',
                             'Copier Margin': p, 'Encryption Period': age})

    df = pd.DataFrame(plot_data)

    # Set up the plot style
    sns.set_style("darkgrid")
    plt.figure(figsize=(12, 8))

    # Create a custom color palette with distinct, visible colors
    num_subnets = len(set(df['Subnet']))
    
    def generate_colors(n):
        base_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', 
            '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8', '#ffbb78', 
            '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d2', '#c7c7c7', 
            '#dbdb8d', '#9edae5', '#393b79', '#637939', '#8c6d31', '#843c39'
        ]
        
        if n <= len(base_colors):
            return base_colors[:n]
        
        additional_colors = []
        for i in range(n - len(base_colors)):
            hue = i / (n - len(base_colors))
            rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.7)  # Reduced saturation and value
            additional_colors.append(mcolors.rgb2hex(rgb))
        
        return base_colors + additional_colors

    colors = generate_colors(num_subnets)
    color_palette = {subnet: color for subnet, color in zip(sorted(set(df['Subnet'])), colors)}

    # Create the plot
    sns.lineplot(data=df, x='Copier Margin', y='Encryption Period',
                 hue='Subnet', marker='o', palette=color_palette)

    # Customize the plot
    plt.title(
        'copier_margin Parameter Influence on Average Delay Length (epochs)',
        fontsize=16, fontweight='bold')
    plt.xlabel('copier_margin (p)', fontsize=12)
    plt.ylabel('Encryption Period (epochs)', fontsize=12)
    plt.legend(title='Subnets', title_fontsize='12', fontsize='10',
               bbox_to_anchor=(1.05, 1), loc='upper left')

    # Ensure y-axis starts at 0
    plt.ylim(bottom=0)

    # Add a light background color
    plt.gca().set_facecolor('#f0f0f0')

    # Adjust layout to prevent cutting off legend
    plt.tight_layout()

    # Save the plot
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(
        output_folder, "avg_black_box_age_vs_copier_margin.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved as {output_path}")


# Directory containing the CSV files
csv_directory: str = 'csv'

# Directory to save the output PNG
output_directory: str = 'examples'

# Process all CSV files
subnet_data: dict[int, DefaultDict[float, list[float]]
                  ] = process_all_csv_files(csv_directory)

# Calculate average ages
avg_data: dict[int, dict[float, float]] = calculate_average_ages(subnet_data)

# Create and save the plot
create_plot(avg_data, output_directory)
