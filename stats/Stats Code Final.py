[4:36 AM] Dhruva Sharma
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, t
import os
import streamlit as st
 
def basic_statistical_analysis_and_plot(ds, sensor_names, selected_stats):
    # Dictionary to store statistics
    stats = {}
 
    # Dictionary to map statistics names to their respective calculation functions
    stats_functions = {
        'mean': np.nanmean,
        'median': np.nanmedian,
        'std_dev': np.nanstd,
        'min': np.nanmin,
        'max': np.nanmax,
        'variance': np.nanvar,
        'skewness': lambda x: skew(x, nan_policy='omit'),
        'kurtosis': lambda x: kurtosis(x, nan_policy='omit'),
        'conf_interval_low': lambda x: t.interval(0.95, len(x)-1, loc=np.nanmean(x), scale=np.nanstd(x)/np.sqrt(len(x)))[0],
        'conf_interval_high': lambda x: t.interval(0.95, len(x)-1, loc=np.nanmean(x), scale=np.nanstd(x)/np.sqrt(len(x)))[1]
    }
 
    for sensor_name in sensor_names:
        if sensor_name in ds.data_vars:
            data = ds[sensor_name].values.flatten()  # Flatten array
 
            # Check if the data is numeric and contains finite values
            if np.issubdtype(data.dtype, np.number):
                data = data[np.isfinite(data)]  # Remove infinite values
 
                # Store the selected statistics
                stats[sensor_name] = {stat: stats_functions[stat](data) for stat in selected_stats}
            else:
                st.write(f"Variable {sensor_name} is not numeric or has unsupported data type.")
        else:
            st.write(f"Variable {sensor_name} is not found in the dataset.")
 
    # Create separate heatmaps for each sensor
    for sensor_name, stat_values in stats.items():
        # Create DataFrame for the current sensor
        stats_df = pd.DataFrame(stat_values, index=[0])
 
        # Plot heatmap for current sensor
        plt.figure(figsize=(10, 6))
        sns.set(font_scale=1.2)  # Adjust font size
        heatmap = sns.heatmap(stats_df, annot=True, cmap='viridis', fmt='.2f', linewidths=0.5, linecolor='white', cbar=True, annot_kws={"size": 8})
        plt.title(f'Statistical Metrics Heatmap for {sensor_name}', fontsize=16)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        st.pyplot(plt)
        plt.close()
 
    return stats
 
def main():
    st.title("Statistical Analysis and Visualization")
    
    file_path = file_selector()
    if not os.path.isfile(file_path):
        st.error(f"Error: File {file_path} does not exist.")
        return
 
    try:
        ds = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')
    except Exception as e:
        st.error(f"Error opening file: {e}")
        return
 
    # List all available sensor names
    available_sensors = list(ds.data_vars.keys())
    selected_sensors = st.multiselect("Select sensor names to analyze:", available_sensors)
 
    # List all available statistics
    available_stats = [
        'mean', 'median', 'std_dev', 'min', 'max', 'variance',
        'skewness', 'kurtosis', 'conf_interval_low', 'conf_interval_high'
    ]
    selected_stats = st.multiselect("Select statistics to calculate:", available_stats)
 
    if st.button("Analyze"):
        if not selected_sensors:
            st.error("Please select at least one sensor.")
        elif not selected_stats:
            st.error("Please select at least one statistical calculation.")
        else:
            stats = basic_statistical_analysis_and_plot(ds, selected_sensors, selected_stats)
 
            # Print the statistics
            if stats:
                for sensor, stat_values in stats.items():
                    st.write(f"Statistics for {sensor}:")
                    for key, value in stat_values.items():
                        st.write(f"{key}: {value}")
                    st.write("")
 
 
def file_selector(folder_path='/home/wvuser/project/data/'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)
 
 
if __name__ == "__main__":
    main()
 
 
