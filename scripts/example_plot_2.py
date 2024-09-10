import os
import csv
from collections import defaultdict
import statistics
import plotly.graph_objects as go
from typing import DefaultDict


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
    fig = go.Figure()

    for subnet, data in avg_data.items():
        p_values: list[float] = sorted(data.keys())
        avg_ages: list[float] = [data[p] for p in p_values]

        fig.add_trace(go.Scatter(
            x=p_values,
            y=avg_ages,
            mode='lines+markers',
            name=f'Subnet {subnet}'
        ))

    fig.update_layout(
        title='Average Black Box Age vs Copier Margin',
        xaxis_title='Copier Margin (p)',
        yaxis_title='Average Black Box Age',
        font=dict(size=12),
        xaxis=dict(type='log'),
        yaxis=dict(type='log'),
        legend_title='Subnets',
        plot_bgcolor='white'
    )

    os.makedirs(output_folder, exist_ok=True)
    output_path: str = os.path.join(
        output_folder, "avg_black_box_age_vs_copier_margin.png")
    fig.write_image(output_path)
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
