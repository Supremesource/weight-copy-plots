import os
import csv
from collections import defaultdict
import statistics
import plotly.graph_objects as go
import numpy as np


def process_csv_file(file_path: str) -> list[float]:
    ages: list[float] = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if float(row['Copier Margin']) == 0:
                ages.append(float(row['Encryption Window Length']))
    return ages


def process_all_csv_files(directory: str) -> dict[int, list[float]]:
    subnet_data: dict[int, list[float]] = {}
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path: str = os.path.join(directory, filename)
            subnet: int = int(filename.split('_')[-1].split('.')[0])
            subnet_data[subnet] = process_csv_file(file_path)
    return subnet_data


def calculate_average_ages(subnet_data: dict[int, list[float]]) -> dict[int, float]:
    return {subnet: statistics.mean(ages) for subnet, ages in subnet_data.items()}


def create_average_age_plot(average_ages: dict[int, float], output_folder: str) -> None:
    subnets: list[int] = sorted(average_ages.keys())
    avg_ages: list[float] = [average_ages[subnet] for subnet in subnets]

    fig = go.Figure(data=[go.Bar(
        x=subnets,
        y=avg_ages,
        text=[f'{age:.2f}' for age in avg_ages],
        textposition='auto',
        marker_color='skyblue',
        marker_line_color='navy',
        marker_line_width=1.5
    )])

    fig.update_layout(
        title='Average Encryption Window Length by Subnet',
        xaxis_title='Subnet',
        yaxis_title='Average Encryption Window Length',
        font=dict(size=12),
        xaxis=dict(tickmode='linear'),
        yaxis=dict(gridcolor='lightgray', gridwidth=0.5),
        plot_bgcolor='white'
    )

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    output_path: str = os.path.join(
        output_folder, "average_black_box_age_by_subnet.png")
    fig.write_image(output_path)
    print(f"Plot saved as {output_path}")


# Directory containing the CSV files
csv_directory: str = 'csv'

# Directory to save the output PNG
output_directory: str = 'examples'

# Process all CSV files
subnet_data: dict[int, list[float]] = process_all_csv_files(csv_directory)

# Calculate average ages
average_ages: dict[int, float] = calculate_average_ages(subnet_data)

# Create and save the plot
create_average_age_plot(average_ages, output_directory)

# Print some overall statistics
all_ages: list[float] = [age for ages in subnet_data.values() for age in ages]
print(f"\nOverall statistics:")
print(
    f"Average Encryption Window Length across all subnets: {statistics.mean(all_ages):.2f}")
print(
    f"Median Encryption Window Length across all subnets: {statistics.median(all_ages):.2f}")
print(f"Maximum Encryption Window Length across all subnets: {max(all_ages):.2f}")
print(f"Minimum Encryption Window Length across all subnets: {min(all_ages):.2f}")
