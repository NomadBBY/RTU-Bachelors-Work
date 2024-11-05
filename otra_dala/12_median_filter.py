import pandas as pd
import numpy as np
import os

# Definē interesējošo frekvenču diapazonus
frequency_ranges = [
    (1687.50, 3750.00),
    (6000.00, 6937.50),
    (9187.50, 10875.00),
    (13125.00, 14812.50),  
    (17062.50, 18937.50),
    (21187.50, 22687.50),
    (24937.50, 26812.50),
    (29062.50, 30937.50),
    (33187.50, 34875.00),
    (37125.00, 38812.50),
    (41062.50, 41812.50),
    (44062.50, 45750.00)
]

# Direktorijas ceļi
input_dir = "/home/arce/csv_output/"
output_dir = "/home/arce/results/final_median_12_ranges/"
anomaly_dir = "/home/arce/results/anomaly_medians/"
os.makedirs(output_dir, exist_ok=True)  # Izveido izejas direktoriju, ja tādas vēl nav
os.makedirs(anomaly_dir, exist_ok=True)  # Izveido anomāliju direktoriju, ja tādas vēl nav

# Inicializē DataFrame, lai turētu apvienotos rezultātus
combined_df = pd.DataFrame({
    'Frekvenču diapazons': [f'No {start:.2f} Hz līdz {end:.2f} Hz' for start, end in frequency_ranges]
})

# Funkcija, lai aprēķinātu medianas noteiktiem frekvenču diapazoniem
def calculate_medians(file_path, file_name):
    # Nolasīt CSV failu
    df = pd.read_csv(file_path)
    
    # Normalizēt kolonnu nosaukumus
    df.columns = df.columns.str.strip()  # Noņem jebkādas vadības simbolus

    # Pārliecinās, ka kolonnu nosaukumi ir pareizi
    if 'Frequency (Hz)' not in df.columns or 'Power spectrum (dB)' not in df.columns:
        raise ValueError("Gaidāmās kolonnas 'Frequency (Hz)' un 'Power spectrum (dB)' netika atrastas CSV failā")
    
    frequency = df['Frequency (Hz)'].values
    motor_noise = df['Power spectrum (dB)'].values
    
    medians = []
    
    # Aprēķina medianu katram diapazonam
    for start_freq, end_freq in frequency_ranges:
        # Filtrē datus noteiktajā diapazonā
        in_range = (frequency >= start_freq) & (frequency <= end_freq)
        range_data = motor_noise[in_range]
        
        # Aprēķina medianu, ja dati ir pieejami šajā diapazonā
        if len(range_data) > 0:
            median_value = np.median(range_data)
        else:
            median_value = np.nan  # vai kāda cita vērtība, lai norādītu, ka nav datu
        
        medians.append(median_value)
    
    # Sagatavo rezultātu kā DataFrame galīgajam iznākumam
    result_df = pd.DataFrame({
        'Frekvenču diapazons': [f'No {start:.2f} Hz līdz {end:.2f} Hz' for start, end in frequency_ranges],
        file_name: medians
    })
    
    # Saglabā rezultātu CSV ar '_result' pieliktu pie faila nosaukuma
    output_file = os.path.join(output_dir, file_name.replace('.csv', '_result.csv'))
    result_df.to_csv(output_file, index=False)
    print(f"Apstrādāts {file_path} un saglabāti rezultāti uz {output_file}")

    # Sagatavo rezultātu kā DataFrame anomāliju medianām
    anomaly_df = pd.DataFrame({
        'Diapazons': [f'Diapazons_{i+1}' for i in range(len(frequency_ranges))],
        'Median Motor Noise (dB)': medians
    })
    
    # Saglabā anomāliju rezultātu CSV
    anomaly_file = os.path.join(anomaly_dir, file_name.replace('.csv', '_anomaly.csv'))
    anomaly_df.to_csv(anomaly_file, index=False)
    print(f"Apstrādāts {file_path} un saglabāti anomāliju rezultāti uz {anomaly_file}")

    return result_df

# Saraksta visus CSV failus ieejas direktorijā
csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

# Apstrādā pirmos 12 failus un apvieno rezultātus
for file_name in csv_files[:12]:
    file_path = os.path.join(input_dir, file_name)
    file_result_df = calculate_medians(file_path, file_name)
    # Apvieno rezultātu apvienotajā DataFrame
    combined_df = pd.merge(combined_df, file_result_df, on='Frekvenču diapazons', how='left')

# Saglabā apvienotos rezultātus uz CSV faila
combined_output_file = os.path.join(output_dir, 'combined_12_median.csv')
combined_df.to_csv(combined_output_file, index=False)
print(f"Apvienotie rezultāti saglabāti uz {combined_output_file}")
