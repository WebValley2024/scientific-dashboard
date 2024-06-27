import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, t
import os

def basic_statistical_analysis_and_plot(file_path, sensor_names):
    if not os.path.isfile(file_path):
        print(f"Error: File {file_path} does not exist.")
        return None

    try:
        ds = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')
    except Exception as e:
        print(f"Error opening file: {e}")
        return None

    # Dictionary to store statistics
    stats = {}

    for sensor_name in sensor_names:
        if sensor_name in ds.data_vars:
            data = ds[sensor_name].values.flatten()  # Flatten array

            # Check if the data is numeric and contains finite values
            if np.issubdtype(data.dtype, np.number):
                data = data[np.isfinite(data)]  # Remove infinite values

                mean_val = np.nanmean(data)
                median_val = np.nanmedian(data)
                std_val = np.nanstd(data)
                min_val = np.nanmin(data)
                max_val = np.nanmax(data)
                var_val = np.nanvar(data)
                skew_val = skew(data, nan_policy='omit')
                kurt_val = kurtosis(data, nan_policy='omit')
                n = len(data)
                se = std_val / np.sqrt(n)
                ci = t.interval(0.95, n-1, loc=mean_val, scale=se)

                # Store the statistics
                stats[sensor_name] = {
                    'mean': mean_val,
                    'median': median_val,
                    'std_dev': std_val,
                    'min': min_val,
                    'max': max_val,
                    'variance': var_val,
                    'skewness': skew_val,
                    'kurtosis': kurt_val,
                    'conf_interval_low': ci[0],
                    'conf_interval_high': ci[1]
                }
            else:
                print(f"Variable {sensor_name} is not numeric or has unsupported data type.")
        else:
            print(f"Variable {sensor_name} is not found in the dataset.")

    # Create separate heatmaps for each sensor
    for sensor_name, stat_values in stats.items():
        # Create DataFrame for the current sensor
        stats_df = pd.DataFrame(stat_values, index=[0])

        # Plot heatmap for current sensor
        plt.figure(figsize=(10, 6))
        sns.set(font_scale=1.2)  # Adjust font size
        heatmap = sns.heatmap(stats_df, annot=True, cmap='viridis', fmt='.2f', linewidths=0.5, linecolor='white', cbar=True, annot_kws={"size": 5})
        plt.title(f'Statistical Metrics Heatmap for {sensor_name}', fontsize=16)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.show()

    return stats

def main():
    file_path = 'data/CSES_01_EFD_1_L02_A1_213330_20211206_164953_20211206_172707_000.h5'

    if not os.path.isfile(file_path):
        print(f"Error: File {file_path} does not exist.")
        return

    try:
        ds = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    # List all available sensor names
    available_sensors = list(ds.data_vars.keys())
    print("Available sensor names:")
    for i, sensor in enumerate(available_sensors, 1):
        print(f"{i}. {sensor}")

    # Allow user to select sensor names or exit
    while True:
        selected_sensors_input = input("Enter the numbers of the sensor names you want to analyze, separated by commas (or type 'exit' to quit): ")
        if selected_sensors_input.lower() == 'exit':
            print("Exiting the program.")
            return
        try:
            selected_sensors_indices = [int(i.strip()) - 1 for i in selected_sensors_input.split(",")]
            selected_sensors = [available_sensors[i] for i in selected_sensors_indices]
            break
        except (ValueError, IndexError) as e:
            print("Invalid input. Please enter the numbers corresponding to the sensor names, separated by commas.")

    stats = basic_statistical_analysis_and_plot(file_path, selected_sensors)

    # Print the statistics
    if stats is not None:
        for sensor, stat_values in stats.items():
            print(f"Statistics for {sensor}:")
            for key, value in stat_values.items():
                print(f"{key}: {value}")
            print()

if __name__ == "__main__":
    main()
