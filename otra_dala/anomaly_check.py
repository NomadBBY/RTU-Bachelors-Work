# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os

# Failu ceļš (aizstājiet ar pareizo ceļu, ja nepieciešams)
file_path = "/home/arce/motor_noise.xlsx"

# Iegūstiet pamatfaila nosaukumu bez paplašinājuma
file_base_name = os.path.splitext(os.path.basename(file_path))[0]

# Nolasiet Excel failu
df = pd.read_excel(file_path)

# Pārliecinieties, ka kolonnu nosaukumi ir pareizi
if 'Frequency (Hz)' in df.columns and 'Motor Noise' in df.columns:
    df = df.rename(columns={'Frequency (Hz)': 'Frequency', 'Motor Noise': 'Motor_Noise'})
elif 'Frequency' not in df.columns or 'Motor_Noise' not in df.columns:
    raise ValueError("Gaidāmās kolonnas 'Frequency (Hz)' un 'Motor Noise' netika atrastas Excel failā")

def motor_noise_analysis(data):
    """
    Veic sekojošas operācijas uz motora troksņa datiem:
    1. Identificē datus piku.
    2. Noņem piku apgabalus, nosakot tos uz NaN.
    3. Atgriež oriģinālos datus, modificētos datus bez pikiem un piku apgabalus.
    """
    # Atrod pikus ar pielāgotu prominenci un attālumu
    peaks, _ = find_peaks(data, prominence=1, distance=10)  # Pielāgojiet šos parametrus pēc nepieciešamības

    # Inicializē masīvu, lai turētu datus bez pikiem
    data_without_peaks = data.copy()
    
    # Iestatiet piku apgabalus (un dažas buferes ap tiem) uz NaN
    buffer = 5  # Punktu skaits ap piku, ko arī iestatīt uz NaN
    peak_regions = []
    for peak in peaks:
        # Pārliecinieties, ka robežas neiziet ārpus diapazona
        start = max(peak - buffer, 0)
        end = min(peak + buffer, len(data) - 1)
        # Saglabā sākuma un beigu indeksus piku apgabalā
        peak_regions.append((start, end))
        # Iestata datus šajā diapazonā uz NaN
        data_without_peaks[start:end+1] = np.nan
    
    return data, data_without_peaks, peak_regions

# Veic analīzi
original_data = df['Motor_Noise'].values
frequency = df['Frequency'].values
original_data, data_without_peaks, peak_regions = motor_noise_analysis(original_data)

# Izveido pirmo figūru
plt.figure(figsize=(12, 6))

# Uzzīmē oriģinālos datus zaļā krāsā
plt.plot(frequency, original_data, color='green', label='Sākotnējie dati')

# Uzzīmē datus bez pikiem sarkanā krāsā
plt.plot(frequency, data_without_peaks, color='red', label='Dati bez pikiem')

# Pievieno marķierus piku apgabalu sākumam un beigām
for start, end in peak_regions:
    plt.scatter(frequency[start], original_data[start], color='green', marker='o', zorder=5, label='Pika Sākums' if start == peak_regions[0][0] else "")
    plt.scatter(frequency[end], original_data[end], color='red', marker='o', zorder=5, label='Pika Beigas' if end == peak_regions[0][1] else "")

plt.legend()
plt.title('Motora troksņa analīze ar noņemtiem pikiem')
plt.xlabel('Frekvence (Hz)')
plt.ylabel('Motora troksnis (dB)')
plt.grid(True)
plt.tight_layout()

# Saglabā pirmo zīmējumu
plot1_save_path = f"/home/arce/results/{file_base_name}_analysis.png"
plt.savefig(plot1_save_path)

# Rāda pirmo zīmējumu
plt.show()

# Izveido otro figūru tikai ar datiem bez pikiem
plt.figure(figsize=(12, 6))

# Uzzīmē datus bez pikiem sarkanā krāsā
plt.plot(frequency, data_without_peaks, color='red', label='Dati bez pikiem')

plt.legend()
plt.title('Motora troksņa analīze: dati bez pikiem')
plt.xlabel('Frekvence (Hz)')
plt.ylabel('Motora troksnis (dB)')
plt.grid(True)
plt.tight_layout()

# Saglabā otro zīmējumu
plot2_save_path = f"/home/arce/results/{file_base_name}_analysis_only_peaks_removed.png"
plt.savefig(plot2_save_path)

# Rāda otro zīmējumu
plt.show()

# ---- Eksportē Ne-NaN Datu Apgabalus uz Teksta Failu ----
# Identificē un eksportē apgabalus, kur dati nav NaN (attiecībā uz "Datiem bez pikiem")
non_nan_regions = []
current_start = None
for i in range(len(data_without_peaks)):
    if not np.isnan(data_without_peaks[i]):
        if current_start is None:
            current_start = i
    else:
        if current_start is not None:
            non_nan_regions.append((frequency[current_start], frequency[i - 1]))
            current_start = None
# Apstrādā gadījumu, kad pēdējais apgabals stiepjas līdz datu beigām
if current_start is not None:
    non_nan_regions.append((frequency[current_start], frequency[-1]))

# Formatē ne-NaN apgabalus teksta izvadei
non_nan_regions_txt = "\n".join([f"No {start:.2f} Hz līdz {end:.2f} Hz" for start, end in non_nan_regions])

# Direktorija ne-NaN apgabalu teksta faila saglabāšanai
txt_dir = "/home/arce/results/non_nan_regions/"
os.makedirs(txt_dir, exist_ok=True)

# Eksportē uz TXT, izmantojot sākotnējā faila nosaukumu
txt_save_path = os.path.join(txt_dir, f"{file_base_name}_non_nan_regions.txt")
with open(txt_save_path, 'w') as f:
    f.write(non_nan_regions_txt)

print(f"Ne-NaN apgabali veiksmīgi eksportēti uz {txt_save_path}!")
