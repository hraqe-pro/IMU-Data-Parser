import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

def read_data_from_file(filename):
    """Reads float data from a text file where values are space-separated."""
    with open(filename, 'r') as file:
        data = []
        for line in file:
            # Split the line by spaces and convert to floats
            values = list(map(float, line.split()))
            data.append(values)
    return np.array(data)

def apply_calibration_correction(data, bias, correction_matrix, calibration_matrix):
    """Applies calibration corrections to the data using bias, correction matrix, and calibration matrix."""
    # Apply bias correction
    biased_data = data - np.array(bias)
    
    # Apply correction matrix
    corrected_data = biased_data @ np.array(correction_matrix).reshape(3, 3).T
    
    # Apply calibration matrix
    calibrated_data = corrected_data @ np.array(calibration_matrix).reshape(3, 3).T

    return calibrated_data

def plot_magnetometer_data(before_data, after_data):
    """Plots the magnetometer data in 3D with both before and after calibration on the same plot."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot before calibration
    ax.scatter(before_data[:, 0], before_data[:, 1], before_data[:, 2], c='r', marker='o', label='Before Calibration')
    
    # Plot after calibration
    ax.scatter(after_data[:, 0], after_data[:, 1], after_data[:, 2], c='b', marker='o', label='After Calibration')
    
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('Magnetometer Data Before and After Calibration')
    ax.legend()
    
    plt.show()

def main():
    # Predefined calibration parameters (replace these with your actual values)
    bias = [2.836979, -1.014804, -3.421376]  # [bias_x, bias_y, bias_z]

    # Example correction matrix (replace with actual values from your calibration)
    correction_matrix = [
        1.194463, 0.000799, 0.002650,
        0.000799, 1.052105, 0.001479,
        0.002650, 0.001479, 1.081255
    ]
    
    # Example calibration matrix (replace with actual values from your calibration)
    calibration_matrix = [
        0.837202, -0.000633, -0.002051,
        -0.000633, 0.950478, -0.001298,
        -0.002051, -0.001298, 0.924858
    ]
    
    while True:
        # Ask the user for the file path
        filename = input("Podaj ścieżkę do pliku z danymi magnetometru: ")
        
        # Check if the file exists
        if os.path.isfile(filename):
            # Read data from file
            data = read_data_from_file(filename)
            
            # Apply calibration
            calibrated_data = apply_calibration_correction(data, bias, correction_matrix, calibration_matrix)
            
            # Plot data before and after calibration
            plot_magnetometer_data(data, calibrated_data)
            break
        else:
            print("Plik nie istnieje. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
