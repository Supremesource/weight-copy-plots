import os
import csv
from collections import defaultdict
import statistics
import matplotlib.pyplot as plt
import numpy as np

def process_csv_file(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            window_length = float(row['Encryption Window Length'])
            data.append(window_length)
    return data

def process_all_csv_files(directory):
    all_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            subnet = int(filename.split('_')[-1].split('.')[0])
            all_data[subnet] = process_csv_file(file_path)
    return all_data

def calculate_average_window_lengths(all_data):
    return {subnet: statistics.mean(lengths) for subnet, lengths in all_data.items()}

def create_bar_plot(optimal_data, non_optimal_data, output_folder):
    plt.figure(figsize=(15, 8))

    subnets = sorted(set(optimal_data.keys()) | set(non_optimal_data.keys()))
    x = np.arange(len(subnets))
    width = 0.35

    optimal_values = [optimal_data.get(subnet, 0) for subnet in subnets]
    non_optimal_values = [non_optimal_data.get(subnet, 0) for subnet in subnets]

    plt.bar(x - width/2, optimal_values, width, label='Optimal', color='blue', alpha=0.7)
    plt.bar(x + width/2, non_optimal_values, width, label='Non-Optimal', color='red', alpha=0.7)

    plt.xlabel('Subnet', fontsize=12)
    plt.ylabel('Average Encryption Window Length', fontsize=12)
    plt.title('Comparison of Average Encryption Window Length by Subnet: Optimal vs Non-Optimal', fontsize=14)
    plt.xticks(x, subnets, rotation=45)
    plt.legend()

    plt.tight_layout()
    output_path = os.path.join(output_folder, "optimal_vs_non_optimal_subnet_comparison.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Bar plot saved as {output_path}")

# Directories
optimal_directory = 'csv/optimal'
non_optimal_directory = 'csv/non-optimal'
output_directory = 'examples'

# Process data
optimal_data = process_all_csv_files(optimal_directory)
non_optimal_data = process_all_csv_files(non_optimal_directory)

# Calculate averages
optimal_avg = calculate_average_window_lengths(optimal_data)
non_optimal_avg = calculate_average_window_lengths(non_optimal_data)

# Create and save the bar plot
create_bar_plot(optimal_avg, non_optimal_avg, output_directory)