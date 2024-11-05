import os
import pandas as pd
import datetime

def process_folder(folder_path):
    # Izveido "data" apakšmapi "/home/arce", ja tā neeksistē
    data_folder = "/home/arce"
    os.makedirs(data_folder, exist_ok=True)
    
    # Inicializē sarakstus, lai glabātu failu nosaukumus un C2 vērtības
    filenames = []
    c2_values = []
    
    # Saņem CSV failu sarakstu mapē un sakārto tos pēc laika zīmogiem faila nosaukumā
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    csv_files.sort(key=lambda f: datetime.datetime.strptime(f.split('.')[0].replace('_', ' '), '%Y %m %d %H-%M-%S'))
    
    # Izvada failu skaitu mapē
    print(f"Number of files in {folder_path}: {len(csv_files)}")
    
    # Iterē cauri visiem sakārtotajiem CSV failiem mapē
    for filename in csv_files:
        file_path = os.path.join(folder_path, filename)
        
        # Ielādē CSV failu pandas DataFrame
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue
        
        # Atrod kolonnu ar 'Value' nosaukumā
        c2_column = next((col for col in df.columns if 'Value' in col), None)
        
        if c2_column is not None:
            # Izvelk datumu un laiku no faila nosaukuma
            date_time_str = filename.split('.')[0].replace('_', ' ')
            date_time = datetime.datetime.strptime(date_time_str, '%Y %m %d %H-%M-%S')
            
            # Izveido jauno faila nosaukuma formātu
            new_filename = date_time.strftime('%Y.%m.%d_%H:%M:%S')
            
            # Pievieno jauno faila nosaukumu un C2 vērtību sarakstiem
            filenames.append(new_filename)
            c2_values.append(df[c2_column].iloc[0])
        else:
            print(f"No 'Value' column found in {filename}")
    
    # Izveido DataFrame ar failu nosaukumiem un C2 vērtībām
    data = {'Filename': filenames, 'C2 Value': c2_values}
    df = pd.DataFrame(data)
    
    # Saglabā DataFrame uz CSV failu mapē "/home/arce"
    csv_path = os.path.join(data_folder, "combined_c2_values.csv")
    df.to_csv(csv_path, index=False)
    
    # Izsauc metodi, lai aprēķinātu stundu medianas
    calculate_hourly_medians(csv_path, data_folder)

def calculate_hourly_medians(csv_path, data_folder):
    # Nolasīt apvienoto CSV failu
    df = pd.read_csv(csv_path)
    
    # Pārvērst 'Filename' kolonnu par datetime formātu
    df['Datetime'] = pd.to_datetime(df['Filename'], format='%Y.%m.%d_%H:%M:%S')
    
    # Iestata 'Datetime' kā DataFrame indeksu
    df.set_index('Datetime', inplace=True)
    
    # Resample datus pēc stundām ('h') un aprēķina 'C2 Value' medianu
    hourly_medians = df['C2 Value'].resample('h').median()
    
    # Izmet rindas ar NaN vērtībām (stundas bez datiem)
    hourly_medians = hourly_medians.dropna()
    
    # Atjauno indeksu, lai iegūtu datumu un laiku atkal kā kolonnu
    hourly_medians = hourly_medians.reset_index()
    
    # Saglabā stundu medianas jaunā CSV failā
    hourly_medians_csv = os.path.join(data_folder, "hourly_medians_c2_values.csv")
    hourly_medians.to_csv(hourly_medians_csv, index=False)
    
    print(f"Hourly medians saved to {hourly_medians_csv}")

# Piemēra izmantošana
folder_path = '/home/arce/csv_output/'
process_folder(folder_path)
