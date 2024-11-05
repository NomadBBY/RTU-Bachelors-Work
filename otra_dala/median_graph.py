import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# Define the file paths
input_file = "/home/arce/results/hourly_medians_c2_values.csv"
output_folder = "/home/arce/results/"

# Read the CSV file
df = pd.read_csv(input_file, parse_dates=['Datetime'], dayfirst=True,
                 date_parser=lambda x: pd.to_datetime(x, format='%d/%m/%Y %H:%M'))

# Sort the dataframe by date
df = df.sort_values('Datetime')

# Increase figure size to accommodate the legend
fig, ax = plt.subplots(figsize=(22, 12))

# Plot the line connecting all points
ax.plot(df['Datetime'], df['C2 Value'], color='gray', alpha=0.5, linewidth=1)

# Create a scatter plot with different colors for each week
for name, group in df.groupby(df['Datetime'].dt.to_period('W')):
    ax.scatter(group['Datetime'], group['C2 Value'], label=name.start_time.strftime('%Y-%m-%d'), alpha=0.7)

# Customize the plot
ax.set_title('Datetime vs C2 Value', fontsize=16)
ax.set_xlabel('Date and Time', fontsize=14)
ax.set_ylabel('C2 Value', fontsize=14)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Format x-axis to show dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
plt.xticks(rotation=45)

# Add legend
ax.legend(title='Week Starting', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add labels for specific events
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
    if event_time in df['Datetime'].values:
        x_pos = df.loc[df['Datetime'] == event_time, 'C2 Value'].values[0]
    else:
        # Use the last known C2 value or a default
        x_pos = df['C2 Value'].iloc[-1]  # or some default value
    ax.annotate(label, (event_time, x_pos), xytext=(10, 0), textcoords='offset points',
                ha='left', va='center', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

plt.tight_layout()
plt.subplots_adjust(right=0.85)  # Adjust this value as needed

# Save the plot
output_file = os.path.join(output_folder, 'c2_value_vs_datetime_plot_legend_moved.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')

print(f"Plot saved as {output_file}")

# Optionally, you can also display the plot
plt.show()
