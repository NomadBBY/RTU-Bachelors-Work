# -*- coding: utf-8 -*-
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def create_output_folder(base_path):
    output_folder = os.path.join(base_path, "median_results")
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def process_folder(folder_path, output_folder):
    filenames = []
    c2_values = []
    
    # Meklē visus CSV failus norādītajā mapē
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    # Sakārto failus pēc datuma
    csv_files.sort(key=lambda f: datetime.datetime.strptime(f.split('.')[0].replace('_', ' '), '%Y %m %d %H-%M-%S'))
    
    print(f"Failu skaits {folder_path}: {len(csv_files)}")
    
    for filename in csv_files:
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        # Atrod kolonnu ar nosaukumu, kas satur 'Value'
        c2_column = next((col for col in df.columns if 'Value' in col), None)
        
        if c2_column is not None:
            date_time_str = filename.split('.')[0].replace('_', ' ')
            date_time = datetime.datetime.strptime(date_time_str, '%Y %m %d %H-%M-%S')
            new_filename = date_time.strftime('%Y.%m.%d_%H:%M:%S')
            filenames.append(new_filename)
            c2_values.append(df[c2_column].iloc[0])
        else:
            print(f"Nav atrasta 'Value' kolonna failā {filename}")
    
    # Izveido DataFrame ar failu nosaukumiem un C2 vērtībām
    data = {'Filename': filenames, 'C2 Value': c2_values}
    df = pd.DataFrame(data)
    
    # Saglabā rezultātus CSV failā
    csv_path = os.path.join(output_folder, "combined_c2_values.csv")
    df.to_csv(csv_path, index=False)
    
    return csv_path

def calculate_hourly_medians(csv_path, output_folder):
    df = pd.read_csv(csv_path)
    # Pārvērš 'Filename' kolonnu par datuma laika formātu
    df['Datetime'] = pd.to_datetime(df['Filename'], format='%Y.%m.%d_%H:%M:%S')
    df.set_index('Datetime', inplace=True)
    
    # Aprēķina stundas mediana
    hourly_medians = df['C2 Value'].resample('h').median().dropna().reset_index()
    
    # Saglabā stundas mediānas rezultātus
    hourly_medians_csv = os.path.join(output_folder, "hourly_medians_c2_values.csv")
    hourly_medians.to_csv(hourly_medians_csv, index=False)
    
    print(f"Stundas mediānas saglabātas {hourly_medians_csv}")
    return hourly_medians_csv

def create_plot(input_file, output_folder):
    df = pd.read_csv(input_file, parse_dates=['Datetime'])
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.sort_values('Datetime')

    fig, ax = plt.subplots(figsize=(22, 12))
    ax.plot(df['C2 Value'], df['Datetime'], color='gray', alpha=0.5, linewidth=1)

    # Grupa pēc nedēļas
    for name, group in df.groupby(df['Datetime'].dt.to_period('W')):
        ax.scatter(group['C2 Value'], group['Datetime'], label=name.start_time.strftime('%Y-%m-%d'), alpha=0.7)

    customize_plot(ax, fig)
    add_events(ax, df)

    plt.tight_layout()
    plt.subplots_adjust(right=0.85)

    output_file = os.path.join(output_folder, 'c2_value_vs_datetime_plot_legend_moved.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Zīmējums saglabāts kā {output_file}")
    plt.show()

def customize_plot(ax, fig):
    ax.set_title('Datums un laiks pret C2 vērtībām', fontsize=16)
    ax.set_xlabel('C2 vērtības', fontsize=14)
    ax.set_ylabel('Datums un laiks', fontsize=14)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.yaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_major_locator(mdates.DayLocator(interval=1))
    fig.autofmt_xdate()
    ax.legend(title='Nedēļas sākums', bbox_to_anchor=(1.05, 1), loc='upper left')

def add_events(ax, df):
    events = [
        ('2024-06-25 09:40', "Pievienots #1 gultnim pulveris, RPM mainīts no 300 uz 430"),
        ('2024-07-09 13:30', "#1 gultnis nedaudz attaukots"),
        ('2024-07-10 14:16', "Uzstādīts jauns #2 gultnis. Iespējami nelieli bojājumi uzstādīšanas laikā."),
        ('2024-07-16 12:00', "Tirs motors: Motors atvienots no gultņa"),
        ('2024-07-16 14:30', "Tirs motors: Pievienota otra ierīce (pelēka)"),
        ('2024-07-16 15:30', "Tirs motors: Otra ierīce nespēj ierakstīt"),
        ('2024-07-16 16:37', "#1 gultnis pilnībā attaukots"),
        ('2024-07-18 17:29', "#1 gultnis ietaukots ar zilo smērvielu"),
        ('2024-07-19 21:11', "#1 gultnim pievienota keramika ar zilo smērvielu"),
        ('2024-07-22 13:34', "Tukša telpa: Testi biroja telpā, bez motora")
    ]

    for date, label in events:
        event_time = pd.to_datetime(date, format='%Y-%m-%d %H:%M')
        y_pos = event_time
        x_pos = df.loc[df['Datetime'] == event_time, 'C2 Value'].values[0] if not df.loc[df['Datetime'] == event_time, 'C2 Value'].empty else ax.get_xlim()[1]
        ax.annotate(label, (x_pos, y_pos), xytext=(10, 0), textcoords='offset points', 
                    ha='left', va='center', fontsize=8, bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

def main():
    base_path = '/home/arce'
    input_folder = os.path.join(base_path, 'csv_output')
    output_folder = create_output_folder(base_path)
    
    csv_path = process_folder(input_folder, output_folder)
    hourly_medians_csv = calculate_hourly_medians(csv_path, output_folder)
    create_plot(hourly_medians_csv, output_folder)

if __name__ == "__main__":
    main()
