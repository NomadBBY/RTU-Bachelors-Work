import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.dates as mdates
import datetime

def create_output_folder(base_path):
    """Creates an output folder to store results."""
    output_folder = os.path.join(base_path, "median_results")
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def process_folder(folder_path, output_folder):
    """Processes CSV files in the specified folder and combines C2 values into a single CSV."""
    filenames = []
    c2_values = []
    
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    csv_files.sort(key=lambda f: datetime.datetime.strptime(f.split('.')[0].replace('_', ' '), '%Y %m %d %H-%M-%S'))
    
    print(f"Number of files in {folder_path}: {len(csv_files)}")
    
    for filename in csv_files:
        try:
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            c2_column = next((col for col in df.columns if 'Value' in col), None)
            
            if c2_column is not None:
                date_time_str = filename.split('.')[0].replace('_', ' ')
                date_time = datetime.datetime.strptime(date_time_str, '%Y %m %d %H-%M-%S')
                new_filename = date_time.strftime('%Y.%m.%d_%H:%M:%S')
                filenames.append(new_filename)
                c2_values.append(df[c2_column].iloc[0])
            else:
                print(f"No 'Value' column found in {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    data = {'Filename': filenames, 'C2 Value': c2_values}
    df = pd.DataFrame(data)
    
    csv_path = os.path.join(output_folder, "combined_c2_values.csv")
    df.to_csv(csv_path, index=False)
    
    return csv_path

def calculate_hourly_medians(csv_path, output_folder):
    """Calculates hourly medians from combined C2 values and saves to CSV."""
    df = pd.read_csv(csv_path)
    df['Datetime'] = pd.to_datetime(df['Filename'], format='%Y.%m.%d_%H:%M:%S')
    df.set_index('Datetime', inplace=True)
    
    hourly_medians = df['C2 Value'].resample('h').median().dropna().reset_index()
    
    hourly_medians_csv = os.path.join(output_folder, "hourly_medians_c2_values.csv")
    hourly_medians.to_csv(hourly_medians_csv, index=False)
    
    print(f"Hourly medians saved to {hourly_medians_csv}")
    return hourly_medians_csv

def save_plot_data(df, output_folder):
    """Saves plot data to CSV for later use."""
    df.to_csv(os.path.join(output_folder, 'c2_value_vs_datetime.csv'), index=False)

def create_plot(input_file, output_folder):
    """Creates a plot of C2 values over time."""
    df = pd.read_csv(input_file, parse_dates=['Datetime'])
    df = df.sort_values('Datetime')

    # Save the data for later use
    save_plot_data(df, output_folder)

    fig, ax = plt.subplots(figsize=(22, 12))
    ax.plot(df['Datetime'], df['C2 Value'], color='gray', alpha=0.5, linewidth=1)

    for name, group in df.groupby(df['Datetime'].dt.to_period('W')):
        ax.scatter(group['Datetime'], group['C2 Value'], label=name.start_time.strftime('%Y-%m-%d'), alpha=0.7)

    customize_plot(ax, fig)
    add_events(ax)

    plt.tight_layout()
    plt.subplots_adjust(right=0.85)

    output_file = os.path.join(output_folder, 'c2_value_vs_datetime_plot_legend_moved.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")
    plt.close(fig)

def customize_plot(ax, fig):
    """Customizes the plot appearance."""
    ax.set_title('Datetime vs C2 Value', fontsize=16)
    ax.set_xlabel('Date and Time', fontsize=14)
    ax.set_ylabel('C2 Value', fontsize=14)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.yaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_major_locator(mdates.DayLocator(interval=1))
    fig.autofmt_xdate()
    ax.legend(title='Week Starting', bbox_to_anchor=(1.05, 1), loc='upper left')

def add_events(ax):
    """Annotates significant events on the plot."""
    events = [
        ('2024-06-25 09:40', "Bearing #1 powder add, RPM change from 300 to 430"),
        ('2024-07-09 13:30', "Bearing #1 bearing degreased slightly"),
        ('2024-07-10 14:16', "Bearing #2 New bearing installed. May be minor damages during installation."),
        ('2024-07-16 12:00', "Pure motor: Motor disconnected from bearing"),
        ('2024-07-16 14:30', "Pure motor: Second Device added (gray)"),
        ('2024-07-16 15:30', "Pure motor: Second Device failed to record"),
        ('2024-07-16 16:37', "Bearing #1 Completely degreased"),
        ('2024-07-18 17:29', "Bearing #1 Greased with blue grease"),
        ('2024-07-19 21:11', "Bearing #1 Added ceramics with blue grease"),
        ('2024-07-22 13:34', "Empty room: Tests in office room, no motor")
    ]
    
    for date, label in events:
        event_time = pd.to_datetime(date, format='%Y-%m-%d %H:%M')
        ax.axvline(event_time, color='red', linestyle='--', alpha=0.5)
        ax.annotate(label, (event_time, ax.get_ylim()[1]), 
                    xytext=(10, 0), textcoords='offset points', 
                    ha='left', va='center', fontsize=8, 
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

def load_combined_data(file_path):
    """Loads combined data from a CSV file."""
    df = pd.read_csv(file_path, parse_dates=['Datetime'])
    return df

def load_range_data(file_path):
    """Loads range data from a CSV file."""
    df = pd.read_csv(file_path, parse_dates=['Datetime'])
    return df

def compute_daily_ranges(df, num_ranges=12):
    """Computes daily ranges for the C2 values."""
    df['Date'] = df['Datetime'].dt.date
    daily_data = df.groupby('Date')['C2 Value'].agg(list).reset_index()
    
    daily_ranges = []
    for _, row in daily_data.iterrows():
        values = np.array(row['C2 Value'])
        percentiles = np.percentile(values, np.linspace(0, 100, num_ranges+1))
        daily_ranges.append(percentiles[1:])  # Exclude the 0th percentile
    
    return daily_data['Date'], daily_ranges

def create_overlay_plot(combined_df, range_df, save_path):
    """Creates an overlay plot of combined C2 values and their ranges."""
    plt.figure(figsize=(14, 8))

    # Plot combined data
    plt.plot(combined_df['Datetime'], combined_df['C2 Value'], color='gray', alpha=0.5, label='C2 Value Over Time')

    # Plot range data
    dates, ranges = compute_daily_ranges(range_df)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(ranges[0])))
    colors = [[c[0], c[1], c[2], 1.0] for c in colors]  # Increase alpha to 1.0 for full opacity
    saturated_cmap = LinearSegmentedColormap.from_list("saturated", colors, N=len(ranges[0]))

    for i in range(len(ranges[0])):
        range_data = [r[i] for r in ranges]
        plt.plot(dates, range_data, marker='o', label=f'Range {i+1}', color=saturated_cmap(i/len(ranges[0])), linewidth=2)

    plt.xlabel('Date')
    plt.ylabel('C2 Value')
    plt.title('C2 Value and Daily Ranges')
    plt.legend(title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
    plt.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Overlay plot saved as {save_path}")
    plt.show()

def main():
    """Main execution function."""
    base_path = '/home/arce'
    input_folder = os.path.join(base_path, 'csv_output')
    output_folder = create_output_folder(base_path)
    
    # Process combined data
    csv_path = process_folder(input_folder, output_folder)
    hourly_medians_csv = calculate_hourly_medians(csv_path, output_folder)
    create_plot(hourly_medians_csv, output_folder)
    
    # Load data for overlay
    combined_file_path = os.path.join(output_folder, 'c2_value_vs_datetime.csv')
    range_file_path = os.path.join(output_folder, 'hourly_medians_c2_values.csv')
    combined_df = load_combined_data(combined_file_path)
    range_df = load_range_data(range_file_path)
    
    # Create overlay plot
    overlay_save_path = os.path.join(output_folder, 'overlayed_c2_value_and_ranges.png')
    create_overlay_plot(combined_df, range_df, overlay_save_path)

if __name__ == "__main__":
    main()
