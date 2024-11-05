import numpy as np
from scipy import signal
import os
import csv
import setproctitle
import pyfftw
import sys

# Definē visas nepieciešamās mainīgās
samp_rate = 96000
buffer_format = np.int16
start_file = "2024_07_05___17-16-15.bin"  # Norādiet sākuma failu

def spectrum(data, segment_size=512):
    fs = samp_rate
    data = data / 32768.0

    noverlap = segment_size // 2
    step = segment_size - noverlap
    shape = (data.size - noverlap) // step, segment_size
    strides = step * data.strides[0], data.strides[0]
    windows = np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)

    window = np.hamming(segment_size)
    windowed_data = windows * window

    fft_data = pyfftw.interfaces.numpy_fft.rfft(windowed_data, n=segment_size)
    Pxx = np.abs(fft_data)**2

    f = np.fft.rfftfreq(segment_size, 1/fs)
    ref = (1 / np.sqrt(2)) ** 2
    p = 10 * np.log10(Pxx / ref)

    return f, p.mean(axis=0)

def save_spectrum_to_csv(input_path, output_path, filename, data):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        frequencies, spectrum_data = spectrum(data)
        
        # Atroda tuvāko frekvenci pie 18000 Hz
        idx_18000 = np.argmin(np.abs(frequencies - 18000))
        value_18000 = spectrum_data[idx_18000]
        
        # Izmanto bin faila nosaukumu (bez paplašinājuma) CSV faila nosaukumam
        csv_filename = os.path.splitext(filename)[0] + '.csv'
        csv_filepath = os.path.join(output_path, csv_filename)
        
        with open(csv_filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Frekvence (Hz)', 'Jaudas spektrs (dB)', '18000 Hz Vērtība'])
            writer.writerow(['', '', f'{value_18000}'])
            for freq, power in zip(frequencies, spectrum_data):
                writer.writerow([freq, power, ''])

        print(f"Spektrs CSV saglabāts: {csv_filepath}")
    except Exception as e:
        print(f"Radās kļūda, veidojot spektra CSV: {e}")

    return csv_filename

def process_bin_files(input_path, output_path):
    setproctitle.setproctitle("FFTProcessor")
    
    # Saraksta visus .bin failus direktorijā
    all_files = [f for f in os.listdir(input_path) if f.endswith('.bin')]
    all_files.sort()  # Sakārto failus apstrādei secībā

    # Izlaiž failus, līdz sasniedz start_file
    start_processing = False
    for filename in all_files:
        if not start_processing:
            if filename == start_file:
                start_processing = True
            else:
                continue
        
        print(f"Apstrādā {filename}")
        
        # Konstruē pilno ceļu uz bināro audio failu
        audio_file_path = os.path.join(input_path, filename)

        # Ielādē bināro audio failu
        with open(audio_file_path, 'rb') as f:
            data = np.frombuffer(f.read(), dtype=buffer_format)

        # Apstrādā datus un saglabā spektru CSV failā
        save_spectrum_to_csv(input_path, output_path, filename, data)

def main(folder_path):
    # Izveido izejas direktoriju lietotāja mājas direktorijā
    home_dir = os.path.expanduser("~")
    output_path = os.path.join(home_dir, 'csv_output')
    os.makedirs(output_path, exist_ok=True)
    
    process_bin_files(folder_path, output_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Izmantošana: python3 graphs.py <ceļš_uz_direktoriju>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    main(folder_path)
