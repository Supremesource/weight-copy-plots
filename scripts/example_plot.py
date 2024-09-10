import os
import csv
from collections import defaultdict
import statistics
import plotly.graph_objects as go
import numpy as np

# Make sure to install the required libraries with these specific versions:
# plotly==5.14.1
# numpy==1.23.5
# kaleido==0.2.1

def process_csv_file(file_path):
    ages = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if float(row['Copier Margin']) == 0:
                ages.append(float(row['Black Box Age']))
    return ages

def process_all_csv_files(directory):
    subnet_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            subnet = int(filename.split('_')[-1].split('.')[0])
            subnet_data[subnet] = process_csv_file(file_path)
    return subnet_data

def calculate_average_ages(subnet_data):
    return {subnet: statistics.mean(ages) for subnet, ages in subnet_data.items()}

def create_average_age_plot(average_ages, output_folder):
    subnets = sorted(average_ages.keys())
    avg_ages = [average_ages[subnet] for subnet in subnets]

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
        title='Average Black Box Age by Subnet',
        xaxis_title='Subnet',
        yaxis_title='Average Black Box Age',
        font=dict(size=12),
        xaxis=dict(tickmode='linear'),
        yaxis=dict(gridcolor='lightgray', gridwidth=0.5),
        plot_bgcolor='white'
    )

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, "average_black_box_age_by_subnet.png")
    fig.write_image(output_path)
    print(f"Plot saved as {output_path}")

# Directory containing the CSV files
csv_directory = 'csv'

# Directory to save the output PNG
output_directory = 'examples'

# Process all CSV files
subnet_data = process_all_csv_files(csv_directory)

# Calculate average ages
average_ages = calculate_average_ages(subnet_data)

# Create and save the plot
create_average_age_plot(average_ages, output_directory)

# Print some overall statistics
all_ages = [age for ages in subnet_data.values() for age in ages]
print(f"\nOverall statistics:")
print(f"Average Black Box Age across all subnets: {statistics.mean(all_ages):.2f}")
print(f"Median Black Box Age across all subnets: {statistics.median(all_ages):.2f}")
print(f"Maximum Black Box Age across all subnets: {max(all_ages):.2f}")
print(f"Minimum Black Box Age across all subnets: {min(all_ages):.2f}")