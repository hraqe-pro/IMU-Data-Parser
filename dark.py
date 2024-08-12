import csv
import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from geopy.distance import geodesic
from scipy.signal import butter, filtfilt

# Funkcja do czytania danych z pliku CSV
def read_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        data = [row for row in reader][1:]  # Pomijamy nagłówki
    return data

# Funkcja do normalizacji danych GPS do metrów
def latlon_to_meters(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters

def normalize_gps_data(gps_data):
    start_lat, start_lon = gps_data[0]
    gps_data_meters = np.zeros((len(gps_data), 3))
    for i, (lat, lon) in enumerate(gps_data):
        gps_data_meters[i, 0] = latlon_to_meters(start_lat, start_lon, lat, start_lon)
        gps_data_meters[i, 1] = latlon_to_meters(start_lat, start_lon, start_lat, lon)
        gps_data_meters[i, 2] = 0  # Zakładamy, że Z = 0 dla GPS
    return gps_data_meters

# Filtr Butterwortha dla przyspieszeń
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data, axis=0)
    return y

# Funkcja do obliczania trajektorii IMU
def calculate_trajectory(imu_data, time_interval=0.1):
    # Przyspieszenia z IMU (ax, ay, az)
    accelerations = imu_data[:, :3]
    
    # Filtracja przyspieszeń
    accelerations = butter_lowpass_filter(accelerations, cutoff=0.1, fs=1/time_interval)
    
    # Prędkości kątowe z IMU (gx, gy, gz)
    angular_velocities = imu_data[:, 3:6]
    
    num_samples = len(accelerations)
    
    # Początkowe położenie i orientacja
    positions = np.zeros((num_samples, 3))
    velocities = np.zeros((num_samples, 3))
    orientation = R.from_euler('xyz', [0, 0, 0], degrees=False)
    
    for i in range(1, num_samples):
        # Obliczanie zmiany orientacji
        delta_orientation = R.from_euler('xyz', angular_velocities[i] * time_interval, degrees=False)
        orientation = orientation * delta_orientation
        
        # Obliczanie przyspieszenia w globalnym układzie odniesienia
        global_acceleration = orientation.apply(accelerations[i])
        
        # Aktualizacja prędkości
        velocities[i] = velocities[i-1] + global_acceleration * time_interval
        
        # Aktualizacja pozycji
        positions[i] = positions[i-1] + velocities[i] * time_interval
    
    return positions

# Funkcja do obliczania trajektorii IMU z magnetometrem
def calculate_trajectory_with_magnetometer(imu_data, magnetometer_data, time_interval=0.1):
    # Przyspieszenia z IMU (ax, ay, az)
    accelerations = imu_data[:, :3]
    
    # Filtracja przyspieszeń
    accelerations = butter_lowpass_filter(accelerations, cutoff=0.1, fs=1/time_interval)
    
    # Prędkości kątowe z IMU (gx, gy, gz)
    angular_velocities = imu_data[:, 3:6]
    
    # Dane z magnetometru (mx, my, mz)
    magnetometer = magnetometer_data[:, :3]
    magnetic_north_declination = magnetometer_data[:, 3]
    
    num_samples = len(accelerations)
    
    # Początkowe położenie i orientacja
    positions = np.zeros((num_samples, 3))
    velocities = np.zeros((num_samples, 3))
    orientation = R.from_euler('xyz', [0, 0, 0], degrees=False)
    
    for i in range(1, num_samples):
        # Obliczanie zmiany orientacji
        delta_orientation = R.from_euler('xyz', angular_velocities[i] * time_interval, degrees=False)
        orientation = orientation * delta_orientation
        
        # Korekcja orientacji na podstawie magnetometru
        magnetic_heading = np.arctan2(magnetometer[i, 1], magnetometer[i, 0]) + magnetic_north_declination[i]
        orientation = R.from_euler('z', magnetic_heading, degrees=False) * orientation
        
        # Obliczanie przyspieszenia w globalnym układzie odniesienia
        global_acceleration = orientation.apply(accelerations[i])
        
        # Aktualizacja prędkości
        velocities[i] = velocities[i-1] + global_acceleration * time_interval
        
        # Aktualizacja pozycji
        positions[i] = positions[i-1] + velocities[i] * time_interval
    
    return positions

# Funkcja do rysowania trajektorii
def plot_data(gps_positions=None, imu_positions=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    if gps_positions is not None:
        ax.plot(gps_positions[:, 0], gps_positions[:, 1], gps_positions[:, 2], 'bo-', label='GPS Trajectory')
        for i in range(len(gps_positions)):
            ax.text(gps_positions[i, 0], gps_positions[i, 1], gps_positions[i, 2], str(i))
    
    if imu_positions is not None:
        ax.plot(imu_positions[:, 0], imu_positions[:, 1], imu_positions[:, 2], 'ro-', label='IMU Trajectory')
        for i in range(len(imu_positions)):
            ax.text(imu_positions[i, 0], imu_positions[i, 1], imu_positions[i, 2], str(i))
    
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters)')
    ax.set_title('Trajektoria GPS i IMU')
    ax.legend()
    
    plt.show()

# Główna funkcja
def main():
    file_path = input("Podaj ścieżkę do pliku CSV: ")
    print(f"Czytam dane z pliku: {file_path}")
    raw_data = read_csv(file_path)
    
    # Dzielimy dane przez 100000000
    gps_data = np.array([[float(row[13])/100000000, float(row[14])/100000000] for row in raw_data])
    imu_data = np.array([[float(val)/100000000 for val in row[:6]] for row in raw_data])
    magnetometer_data = np.array([[float(row[6])/100000000, float(row[7])/100000000, float(row[8])/100000000, float(row[9])/100000000] for row in raw_data])
    
    gps_data_meters = normalize_gps_data(gps_data)
    imu_positions = calculate_trajectory(imu_data)
    imu_mag_positions = calculate_trajectory_with_magnetometer(imu_data, magnetometer_data)
    
    while True:
        print("Wybierz opcję wyświetlania:")
        print("1 - Tylko dane z GPS")
        print("2 - Tylko dane z IMU")
        print("3 - Dane z GPS i IMU")
        print("4 - Dane z IMU i magnetometru")
        option = input("Wybierz opcję (1/2/3/4): ")
        
        if option == '1':
            plot_data(gps_positions=gps_data_meters)
            break
        elif option == '2':
            plot_data(imu_positions=imu_positions)
            break
        elif option == '3':
            plot_data(gps_positions=gps_data_meters, imu_positions=imu_positions)
            break
        elif option == '4':
            plot_data(imu_positions=imu_mag_positions)
            break
        else:
            print("Nieprawidłowa opcja. Spróbuj ponownie.")

if __name__ == "__main__":
    main()









