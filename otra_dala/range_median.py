import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from datetime import datetime
from matplotlib.colors import LinearSegmentedColormap

def compute_median_ranges(data, num_ranges=12):
    """Computes median values of the data split into specified number of ranges."""
    filtered_data = data[~np.isnan(data)]
    split_indices = np.array_split(np.arange(len(filtered_data)), num_ranges)
    medians = [np.median(filtered_data[indices]) for indices in split_indices]
    return medians

def extract_date(filename):
    """Extracts date from filename in the format YYYY_MM_DD___HH-MM-SS_anomaly.csv."""
    try:
        date_str = filename.split('___')[0]
        return datetime.strptime(date_str, '%Y_%m_%d')
    except (ValueError, IndexError) as e:
        print(f"Unable to extract date from filename: {filename}. Error: {e}")
        return None

# Folder containing the CSV files
folder_path = "/home/arce/results/anomaly_medians/"
file_paths = glob.glob(os.path.join(folder_path, "*.csv"))

all_medians = []
file_dates = []

for file_path in file_paths:
    file_base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    try:
        df = pd.read_csv(file_path)
        
        if 'Range' not in df.columns or 'Median Motor Noise (dB)' not in df.columns:
            print(f"Skipping file {file_base_name}: Expected 'Range' or 'Median Motor Noise (dB)' column not found")
            continue
        
        median_values = df['Median Motor Noise (dB)'].values
        medians = compute_median_ranges(median_values, num_ranges=12)
        
        date = extract_date(file_base_name)
        if date is not None:
            all_medians.append(medians)
            file_dates.append(date)
        else:
            print(f"Skipping file {file_base_name}: Unable to extract date")
    except Exception as e:
        print(f"Error processing file {file_base_name}: {e}")

if not file_dates:
    print("No valid data to plot. Please check your file names and data.")
    exit()

# Sort data by date
sorted_data = sorted(zip(file_dates, all_medians))
file_dates, all_medians = zip(*sorted_data)

# Convert to DataFrame for plotting
medians_df = pd.DataFrame(all_medians, index=file_dates, columns=[f'Range_{i+1}' for i in range(12)])

# Create a custom colormap with more saturated colors
colors = plt.cm.rainbow(np.linspace(0, 1, 12))
colors = [[c[0], c[1], c[2], 1.0] for c in colors]  # Increase alpha to 1.0 for full opacity
saturated_cmap = LinearSegmentedColormap.from_list("saturated", colors, N=12)

# Plotting
plt.figure(figsize=(14, 8))
for i in range(12):
    range_data = medians_df[f'Range_{i+1}']
    plt.plot(file_dates, range_data, marker='o', label=f'Region {i+1}', color=saturated_cmap(i/12), linewidth=2)

plt.xlabel('Date')
plt.ylabel('Median Motor Noise (dB)')
plt.title('Motor Noise Across Files')
plt.legend(title='Regions', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
plt.tight_layout()

# Save the plot
plot_save_path = "/home/arce/results/median_motor_noise_across_files.png"
os.makedirs(os.path.dirname(plot_save_path), exist_ok=True)
plt.savefig(plot_save_path, dpi=300)

# Show the plot
plt.show()
print(f"Plot saved to {plot_save_path}!")
