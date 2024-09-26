import os
import csv
from collections import defaultdict
import statistics
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors as mcolors
import colorsys
import numpy as np
from scipy.interpolate import interp1d
from typing import DefaultDict
import re


def process_csv_file(file_path: str) -> DefaultDict[float, list[float]]:
    data: DefaultDict[float, list[float]] = defaultdict(list)
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            p: float = float(row['Copier Margin'])
            age: float = float(row['Encryption Window Length'])
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

    # Calculate the average encryption period across all subnets
    avg_encryption_period = df.groupby('Copier Margin')[
        'Encryption Period'].mean().reset_index()

    # Set up the plot style
    sns.set_style("whitegrid")
    fig, ax1 = plt.subplots(figsize=(24, 14))  # Increased figure size

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
            rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.7)
            additional_colors.append(mcolors.rgb2hex(rgb))

        return base_colors + additional_colors

    colors = generate_colors(num_subnets)
    color_palette = {subnet: color for subnet,
                     color in zip(sorted(set(df['Subnet'])), colors)}

    # Create the plot with increased alpha for individual subnet lines
    sns.lineplot(data=df, x='Copier Margin', y='Encryption Period',
                 hue='Subnet', marker='o', palette=color_palette, alpha=1.0, ax=ax1)

    # Plot the average line
    avg_line = ax1.plot(avg_encryption_period['Copier Margin'], avg_encryption_period['Encryption Period'],
                        color='black', linewidth=3, label='Average')

    # Customize the plot
    ax1.set_title('copier_margin Parameter Influence on Average Delay Length (epochs)',
                  fontsize=20, fontweight='bold')
    ax1.set_xlabel('copier_margin (p)', fontsize=16)
    ax1.set_ylabel('Encryption Period (epochs)', fontsize=16)
    ax1.tick_params(axis='both', which='major', labelsize=14)

    # Create custom legends
    subnet_handles, subnet_labels = ax1.get_legend_handles_labels()

    # Sort subnets numerically
    def extract_subnet_number(label):
        match = re.search(r'Subnet (\d+)', label)
        return int(match.group(1)) if match else 0

    sorted_subnets = sorted(zip(subnet_handles, subnet_labels),
                            key=lambda x: extract_subnet_number(x[1]))
    subnet_handles, subnet_labels = zip(*sorted_subnets)

    # Remove the auto-generated legend
    ax1.get_legend().remove()

    # Create separate legend for subnets outside the plot with larger font size
    fig.subplots_adjust(right=0.65)  # Make even more room for the legend
    subnet_legend = fig.legend(subnet_handles, subnet_labels, loc='center right',
                               bbox_to_anchor=(1.0, 0.5), fontsize=14, title='Subnets',
                               title_fontsize=18, ncol=1, borderaxespad=0.)

    # Create legend for Average line with larger font size
    ax1.legend(avg_line, ['Average'], loc='upper right', fontsize=16)

    # Ensure y-axis starts at 0
    ax1.set_ylim(bottom=0)

    # Add a light background color
    ax1.set_facecolor('#f0f0f0')

    # Adjust layout to prevent cutting off legends
    plt.tight_layout()

    # Save the plot
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(
        output_folder, "avg_black_box_age_vs_copier_margin_with_average.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved as {output_path}")


# Directory containing the CSV files
csv_directory: str = 'csv/optimal'

# Directory to save the output PNG
output_directory: str = 'examples'

# Process all CSV files
subnet_data: dict[int, DefaultDict[float, list[float]]
                  ] = process_all_csv_files(csv_directory)

# Calculate average ages
avg_data: dict[int, dict[float, float]] = calculate_average_ages(subnet_data)

# Create and save the plot
create_plot(avg_data, output_directory)
