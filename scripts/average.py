import csv
import os

def process_csv_files(directory):
    total_black_box_age = 0
    total_rows = 0

    # Iterate through all CSV files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                
                for row in csv_reader:
                    copier_margin = float(row['Copier Margin'])
                    
                    # Process only rows where copier margin is 0
                    if copier_margin == 0:
                        black_box_age = int(row['Black Box Age'])
                        total_black_box_age += black_box_age
                        total_rows += 1

    # Calculate the average
    if total_rows > 0:
        average_black_box_age = total_black_box_age / total_rows
        return average_black_box_age
    else:
        return 0

# Directory containing the CSV files
csv_directory = 'csv'

# Calculate the average Black Box Age
average = process_csv_files(csv_directory)

print(f"The average Black Box Age (for copier margin 0) is: {average:.2f}")