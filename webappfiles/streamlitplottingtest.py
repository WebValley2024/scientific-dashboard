import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, t
import xarray as xr
import pandas as pd
import os
from plotly.subplots import make_subplots
import plotly.graph_objs as go

import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import h5py
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from shapely import geometry
from glob import glob
import datetime

folder_path = '/home/wvuser/project/data'
project_dir = '/home/wvuser/project/data'

EFD1 = 'CSES_01_EFD_1_L02_A1_213330_20211206_164953_20211206_172707_000.h5'
HEP1 = 'CSES_01_HEP_1_L02_A4_176401_20210407_182209_20210407_190029_000.h5'
HEP4 = 'CSES_01_HEP_4_L02_A4_202091_20210923_184621_20210923_192441_000.h5'
LAP1 = 'CSES_01_LAP_1_L02_A3_174201_20210324_070216_20210324_073942_000.h5'
SCM1 = 'CSES_01_SCM_1_L02_A2_183380_20210523_154551_20210523_162126_000.h5'
HEPD = 'CSES_HEP_DDD_0219741_20220117_214156_20220117_230638_L3_0000267631.h5'


def dataset(path):
    return xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')
 
# Function to list all variable names in a dataset
def variables(data):
    return list(data.keys())

file_list = [
    os.path.join(project_dir, EFD1),
    os.path.join(project_dir, HEP1),
    os.path.join(project_dir, HEP4),
    os.path.join(project_dir, LAP1),
    os.path.join(project_dir, SCM1),
    os.path.join(project_dir, HEPD)
]
# Function to calculate leftmost and rightmost latitude extremes
def calculate_extremes(coordinates):
    if coordinates:
        min_lat = min(point[1] for point in coordinates[0])
        max_lat = max(point[1] for point in coordinates[0])
        return min_lat, max_lat
    return None, None

# Function for basic statistical analysis and plot
# def basic_statistical_analysis_and_plot(ds, sensor_names, selected_stats):
#     stats = {}
#     stats_functions = {
#         'mean': np.nanmean,
#         'median': np.nanmedian,
#         'std_dev': np.nanstd,
#         'min': np.nanmin,
#         'max': np.nanmax,
#         'variance': np.nanvar,
#         'skewness': lambda x: skew(x, nan_policy='omit'),
#         'kurtosis': lambda x: kurtosis(x, nan_policy='omit'),
#         'conf_interval_low': lambda x: t.interval(0.95, len(x)-1, loc=np.nanmean(x), scale=np.nanstd(x)/np.sqrt(len(x)))[0],
#         'conf_interval_high': lambda x: t.interval(0.95, len(x)-1, loc=np.nanmean(x), scale=np.nanstd(x)/np.sqrt(len(x)))[1]
#     }

#     for sensor_name in sensor_names:
#         if sensor_name in ds.data_vars:
#             data = ds[sensor_name].values.flatten()  # Flatten array

#             if np.issubdtype(data.dtype, np.number):
#                 data = data[np.isfinite(data)]  # Remove infinite values
#                 stats[sensor_name] = {stat: stats_functions[stat](data) for stat in selected_stats}
#             else:
#                 st.write(f"Variable {sensor_name} is not numeric or has unsupported data type.")
#         else:
#             st.write(f"Variable {sensor_name} is not found in the dataset.")

#     for sensor_name, stat_values in stats.items():
#         stats_df = pd.DataFrame(stat_values, index=[0])
#         fig, ax = plt.subplots(figsize=(10, 6))
#         sns.set(font_scale=1.2)
#         heatmap = sns.heatmap(stats_df, annot=True, cmap='viridis', fmt='.2f', linewidths=0.5, linecolor='white', cbar=True, annot_kws={"size": 8}, ax=ax)
#         ax.set_title(f'Statistical Metrics Heatmap for {sensor_name}', fontsize=16)
#         plt.xticks(rotation=45)
#         plt.yticks(rotation=0)
#         plt.tight_layout()
#         st.pyplot(fig)
#         plt.close(fig)

#     return stats

# Function for file selection
# def file_selector():
#     folder_path = '/home/wvuser/project/data'
#     filenames = os.listdir(folder_path)
#     selected_filename = st.selectbox('Select a file', filenames)
#     return os.path.join(folder_path, selected_filename)

# Function for map drawing
def draw_map():
    # print('asdasdakjsdnas')
    st.header("Draw Rectangles on Map")
    m = folium.Map(location=[45.5236, -122.6750], zoom_start=1.5)
    draw = Draw(
        draw_options={
            'polyline': False,
            'polygon': True,
            'circle': False,
            'marker': False,
            'circlemarker': False,
            'rectangle': True,
        }
    )
    draw.add_to(m)
    st_map = st_folium(m, width=700, height=500)

    last_active_drawing = st_map.get('last_active_drawing')
    if last_active_drawing:
        geometry = last_active_drawing.get('geometry')
        if geometry and 'coordinates' in geometry:
            coordinates = geometry['coordinates']
            st.write("Coordinates of the last active drawing:")
            for point in coordinates[0]:  # Assuming it's a polygon and accessing the outer ring
                lng, lat = point
                st.write(f"Longitude: {lng}, Latitude: {lat}")
            
            coords = geometry['coordinates'][0]  # Access the first inner list
       
            coords = coords[:-1]
            st.write(coords)
            print(coords)
            #call function and pass coords and file path
            pathskidibidi = polygon(coords, file_list[:-1])
            st.write(polygon(coords, file_list[:-1]))
            print('file path list')
            print(pathskidibidi)

            dataset_type = extract_dataset_type(pathskidibidi)
            print(dataset_type)

            for dataset in dataset_type:
                file_path = dataset[0]
                dataset_type = dataset[1]
                file_name = file_path.split('/')[-1]
                
                if dataset_type == 'EFD':
                    plot_EFD(file_path)
                elif dataset_type == 'LAP':
                    # plot_twin_timeline_verse_time(file_path)
                    plot_twin_timeline_utc(file_path)
                    plot_on_map_density(file_path)
                    plot_on_map_temperature(file_path)

                    
            print(polygon(coords, file_list[:-1]))
            min_lat, max_lat = calculate_extremes(coordinates)
            st.write(f"Leftmost Latitude: {min_lat:.6f}")
            st.write(f"Rightmost Latitude: {max_lat:.6f}")


        else:
            st.write("No 'coordinates' found in 'geometry'.")
    else:
        st.write("No 'last_active_drawing' found in st_map.")

# Function for statistical analysis
# def statistical_analysis():
#     st.header("Statistical Analysis and Visualization")
#     # folder_path = st.text_input("Enter the folder path:", '/home/wvuser/project/data')
#     if folder_path:
#         file_path = file_selector()
#         if not os.path.isfile(file_path):
#             st.error(f"Error: File {file_path} does not exist.")
#             return

#         try:
#             ds = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')
#             st.write("Dataset loaded successfully.")
#         except Exception as e:
#             st.error(f"Error opening file: {e}")
#             return

#         available_sensors = list(ds.data_vars.keys())
#         selected_sensors = st.multiselect("Select sensor names to analyze:", available_sensors)

#         available_stats = [
#             'mean', 'median', 'std_dev', 'min', 'max', 'variance', 
#             'skewness', 'kurtosis', 'conf_interval_low', 'conf_interval_high'
#         ]
#         selected_stats = st.multiselect("Select statistics to calculate:", available_stats)

#         if st.button("Analyze"):
#             if not selected_sensors:
#                 st.error("Please select at least one sensor.")
#             elif not selected_stats:
#                 st.error("Please select at least one statistical calculation.")
#             else:
#                 stats = basic_statistical_analysis_and_plot(ds, selected_sensors, selected_stats)
#                 if stats:
#                     for sensor, stat_values in stats.items():
#                         st.write(f"Statistics for {sensor}:")
#                         for key, value in stat_values.items():
#                             st.write(f"{key}: {value}")
#                         st.write("")


# def filter_data_within_coordinates(coordinates, file_path):
#     try:
#         ds = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')
#         st.write("Dataset loaded successfully.")
#     except Exception as e:
#         st.error(f"Error opening file: {e}")
#         return None

#     # Ensure the dataset contains GEO_LAT and GEO_LON
#     if 'GEO_LAT' not in ds or 'GEO_LON' not in ds:
#         st.error("Dataset does not contain GEO_LAT and GEO_LON variables.")
#         return None

#     geo_lat = ds['GEO_LAT']
#     geo_lon = ds['GEO_LON']

#     # Extract latitude and longitude boundaries from coordinates
#     min_lon = min(point[0] for point in coordinates)
#     max_lon = max(point[0] for point in coordinates)
#     min_lat = min(point[1] for point in coordinates)
#     max_lat = max(point[1] for point in coordinates)

#     # Filter data within the coordinate boundaries
#     lat_filter = (geo_lat >= min_lat) & (geo_lat <= max_lat)
#     lon_filter = (geo_lon >= min_lon) & (geo_lon <= max_lon)
#     combined_filter = lat_filter & lon_filter

#     # Convert the combined filter to a DataArray
#     combined_filter_da = xr.DataArray(combined_filter, dims=geo_lat.dims, coords=geo_lat.coords)

#     # Apply filter to dataset
#     filtered_ds = ds.where(combined_filter_da, drop=True)

#     # Check if there are any valid data points left after filtering
#     if filtered_ds.sizes['time'] == 0:  # Adjust 'time' dimension if necessary
#         st.error("No data points found within the specified coordinates.")
#         return None

#     return filtered_ds



def polygon(points, files):    
    intersectionFile = []
 
    latitudes = [point[1] for point in points]
    longitudes = [point[0] for point in points]

    latitudes.pop()
    longitudes.pop()
 
    lat_min = min(latitudes)
    lat_max = max(latitudes)
    lon_min = min(longitudes)
    lon_max = max(longitudes)
 
    for file in files:
 
        ds = dataset(file)
        geo_lat = ds.GEO_LAT
        geo_lon = ds.GEO_LON
 
        lat_mask = (geo_lat >= lat_min) & (geo_lat <= lat_max)
        lon_mask = (geo_lon >= lon_min) & (geo_lon <= lon_max)
 
        final_mask = lat_mask & lon_mask
 
        if final_mask.any():
            intersectionFile.append(file)
            st.write('SONO QUI ')
    return intersectionFile


def reduce_frequency(data_array, frequency):
    """
    Reduce the number of measurements in each row of the xarray based on the specified frequency,
    while preserving the metadata.
    Parameters:
    data_array (xarray.DataArray): The input xarray.
    frequency (int): The number of elements to keep in each row.
    Returns:
    xarray.DataArray: The reduced xarray.
    """
    num_rows, num_cols = data_array.shape
    if frequency > num_cols:
        raise ValueError("Frequency cannot be greater than the number of columns in the data array.")
    reduced_rows = []
    for row in data_array.values:
        indices = np.linspace(0, num_cols - 1, frequency, dtype=int)
        reduced_row = row[indices]
        reduced_rows.append(reduced_row)
    reduced_values = np.stack(reduced_rows, axis=0)
    reduced_data_array = xr.DataArray(reduced_values,
                                      dims=[data_array.dims[0], 'reduced_freq'],
                                      coords={data_array.dims[0]: data_array.coords[data_array.dims[0]],
                                              'reduced_freq': indices},
                                      attrs=data_array.attrs)
    return reduced_data_array
 
 
def plot_EFD(path):
    f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims='sort')
    X_Waveform = f['A111_W'][...]
    Y_Waveform = f['A112_W'][...]
    Z_Waveform = f['A113_W'][...]
    verse_time = f['VERSE_TIME'][...].values.flatten()
    X_Power_spectrum = f['A111_P'][...]
    Y_Power_spectrum = f['A112_P'][...]
    Z_Power_spectrum = f['A113_P'][...]
    latitude = f['MAG_LAT'][...]
    longitude = f['MAG_LON'][...]
    frequency = f['FREQ'][...]
    magnitude = np.sqrt(X_Waveform**2 + Y_Waveform**2 + Z_Waveform**2)
    polar_angle = np.arccos(Z_Waveform / magnitude)  # theta
    azimuthal_angle = np.arctan2(Y_Waveform, X_Waveform)  # phi
 
    # Convert angles to degrees
    polar_angle = np.degrees(polar_angle)
    azimuthal_angle = np.degrees(azimuthal_angle)
 
    reduced_freq = 100  # Specify the desired frequency here
    X_Waveform = reduce_frequency(X_Waveform, reduced_freq)
    Y_Waveform = reduce_frequency(Y_Waveform, reduced_freq)
    Z_Waveform = reduce_frequency(Z_Waveform, reduced_freq)
    magnitude = reduce_frequency(magnitude, reduced_freq)
    polar_angle = reduce_frequency(polar_angle, reduced_freq)
    azimuthal_angle = reduce_frequency(azimuthal_angle, reduced_freq)
 
    X_Waveform = X_Waveform.values.flatten()
    Y_Waveform = Y_Waveform.values.flatten()
    Z_Waveform = Z_Waveform.values.flatten()
    magnitude = magnitude.values.flatten()
    polar_angle = polar_angle.values.flatten()
    azimuthal_angle = azimuthal_angle.values.flatten()
 
    len_time = len(verse_time)
 
    # Ensure vers_extend has the same length as the waveforms
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], reduced_freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], reduced_freq)])
    # First figure for waveforms and magnitude
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=vers_extend, y=X_Waveform, mode='lines', name='X Waveform'))
    fig1.add_trace(go.Scatter(x=vers_extend, y=Y_Waveform, mode='lines', name='Y Waveform'))
    fig1.add_trace(go.Scatter(x=vers_extend, y=Z_Waveform, mode='lines', name='Z Waveform'))
    fig1.add_trace(go.Scatter(x=vers_extend, y=magnitude, mode='lines', name='Vector sum'))
 
    fig1.update_layout(
        title="X, Y, Z Waveforms and the Vector Sum",
        xaxis_title="Time (ms)",
        yaxis_title="V/m",
        legend=dict(x=1, y=0.5)
    )
 
    # Second figure for polar and azimuthal angles
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=vers_extend, y=polar_angle, mode='lines', name='Polar Angle', yaxis='y2'))
    fig2.add_trace(go.Scatter(x=vers_extend, y=azimuthal_angle, mode='lines', name='Azimuthal Angle', yaxis='y3'))
 
    fig2.update_layout(
        title="Polar and Azimuthal Angles",
        xaxis_title="Time (ms)",
        yaxis2=dict(
            title="Polar Angle (degrees)",
            range=[0, 180],
            side='left'
        ),
        yaxis3=dict(
            title="Azimuthal Angle (degrees)",
            range=[0, 360],
            overlaying='y2',
            side='right'
        ),
        legend=dict(x=1.08, y=0.54)
    )
 
    # Third figure for power spectra
    power_spectra = {'X': X_Power_spectrum, 'Y': Y_Power_spectrum, 'Z': Z_Power_spectrum}
    for axis, spectrum in power_spectra.items():
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=np.log10(spectrum.values.T),  # Apply log10 to intensity (z-axis)
            x=verse_time,
            y=frequency,
            colorscale='Viridis',
            colorbar=dict(title='Log Power Spectrum')
        ))
        fig.update_layout(
            title=f"{axis} Power Spectrum",
            xaxis_title="Time (ms)",
            yaxis_title="Frequency (Hz)",
            legend=dict(x=1, y=0.5)
        )
        
        st.plotly_chart(fig)
 
    # Display the first two figures
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    

# def plot_twin_timeline_verse_time(path):
#     f = xr.open_dataset(path)
#     time = f.VERSE_TIME
#     data = f.A311
#     data2 = f.A321
#     data = reduce_frequency(data, 1)
#     data2 = reduce_frequency(data2, 1)
#     log = True
#     #catch all problems with frequency
#     try:
#         freq = data.shape[1]
#     except:
#         freq = 1
 
#     #remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
#     data=data.values[1:].flatten()
#     data2 = data2.values[1:].flatten()
 
#     #do the same with the verse time
#     verse_time = verse_time.values[1:].flatten()
#     #get the length to be able to plot it
#     len_time = len(verse_time)
 
#     #plot everything
#     vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
#     vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
 
#     # Create subplots with a secondary y-axis
#     fig = make_subplots(specs=[[{"secondary_y": True}]])

#     # Add trace for the data
#     fig.add_trace(
#         go.Scatter(x=vers_extend, y=data, name="Electron Density", line=dict(color='blue')),
#         secondary_y=False
#     )
#     fig.add_trace(
#     go.Scatter(x=vers_extend, y=data2, name="Electron Temperature", line=dict(color='red')),
#     secondary_y=True,  # y-axis on RHS
# )

#     # Configure y-axes
#     fig.update_yaxes(title_text="1/m^3", secondary_y=False)
#     fig.update_yaxes(title_text = "K", secondary_y=True)
#     if log:
#         fig.update_yaxes(type="log", secondary_y=False)
#         fig.update_yaxes(type="log", secondary_y=True)


#     # Configure x-axis
#     fig.update_xaxes(title_text="ms")

#     # Configure layout
#     fig.update_layout(
#         title="Electron Density and Temperature",
#         template="plotly_white",
#         autosize=False,
#         width=800,
#         height=600,
#     )

#     # Show the figure
#     fig.show()



def extract_dataset_type(file_paths):    
    dataset_types = []
    
    for file_path in file_paths:
        file_name = file_path.split('/')[-1]
        
        if 'EFD' in file_name:
            dataset_types.append([file_path, 'EFD'])
        elif 'LAP' in file_name:
            dataset_types.append([file_path, 'LAP'])
        else:
            raise ValueError(f"Unknown dataset type in file name: {file_name}")
    
    return dataset_types

def plot_twin_timeline_verse_time(path):
    # Open the dataset using the h5netcdf engine
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    
    # Extract the required variables
    verse_time = f['VERSE_TIME'][...].values.flatten()
    data = f['A311'][...]
    data2 = f['A321'][...]
    
    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)
    data2 = reduce_frequency(data2, 1)
    
    log = True
    
    # Get the frequency dimension
    try:
        freq = data.shape[1]
    except:
        freq = 1
    
    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[1:].flatten()
    data2 = data2.values[1:].flatten()
    
    # Remove the first element of the verse time and flatten it
    verse_time = verse_time[1:]
    
    # Get the length to be able to plot it
    len_time = len(verse_time)
    
    # Plot everything
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
    
    # Create subplots with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add trace for the data
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data, name="Electron Density", line=dict(color='blue')),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data2, name="Electron Temperature", line=dict(color='red')),
        secondary_y=True  # y-axis on RHS
    )
    
    # Configure y-axes
    fig.update_yaxes(title_text="1/m^3", secondary_y=False)
    fig.update_yaxes(title_text="K", secondary_y=True)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)
        fig.update_yaxes(type="log", secondary_y=True)
    
    # Configure x-axis
    fig.update_xaxes(title_text="ms")
    
    # Configure layout
    fig.update_layout(
        title="Electron Density and Temperature",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )
    
    # Show the figure
    st.plotly_chart(fig)


def plot_twin_timeline_utc(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    
    # Extract the required variables
    time = f['UTC_TIME'][...].values.flatten()
    data = f['A311'][...]
    data2 = f['A321'][...]
    
    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)
    data2 = reduce_frequency(data2, 1)
    
    log = True

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
    
    # Remove the first element of the data and flatten it to be able to plot it
    data = data.values[1:].flatten()
    data2 = data2.values[1:].flatten()
    
    # Remove the first element of the time and flatten it
    time = time[1:]
    
    len_time = len(time)
    time_extend = np.concatenate([np.linspace(time[i], time[i+1], freq, endpoint=False) for i in range(len_time - 1)])
    time_extend = np.concatenate([time_extend, np.linspace(time[-2], time[-1], freq)])
    utctimes = convert_to_utc_time(time_extend)
    
    df = pd.DataFrame({
        "data": data,
        "data2": data2,
        "time": utctimes
    })

    # Plotting with Plotly
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Electron Density'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['time'], y=df['data2'], mode='lines', name='Electron Temperature', line=dict(color='red')), secondary_y=True)

    # Update y-axes titles
    fig.update_yaxes(title_text="1/m^3", secondary_y=False)
    fig.update_yaxes(title_text="K", secondary_y=True)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)
        fig.update_yaxes(type="log", secondary_y=True)

    # Update x-axis title
    fig.update_xaxes(title_text="Time (UTC)")

    # Update layout
    fig.update_layout(
        title="Electron Temperature and Density",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600
    )

    # Show the figure
    st.plotly_chart(fig)


def plot_on_map_density(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    
    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    longitude = f['GEO_LON'][...]
    data = f['A311'][...]

    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    try:
        freq = data.shape[1]
    except:
        freq = 1

    measure = data.values[1:].flatten()
    lon = longitude.values[1:].flatten()
    lat = latitude.values[1:].flatten()
    
    length_coord = len(lon)
    length_measure = len(measure)

    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
    
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    fig = go.Figure()

    scatter = go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        text=measure,
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="1/m^3"),
            cmin=measure.min(),
            cmax=10**11,
            showscale=True
        ),
        mode='markers'
    )

    fig.add_trace(scatter)

    # Update the layout
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="lightgrey",
        ),
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_layout(title="Electron Density", template="plotly_white")

    # Show the figure
    st.plotly_chart(fig)


def plot_on_map_temperature(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    
    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    longitude = f['GEO_LON'][...]
    data = f['A321'][...]

    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    try:
        freq = data.shape[1]
    except:
        freq = 1

    measure = data.values[1:].flatten()
    lon = longitude.values[1:].flatten()
    lat = latitude.values[1:].flatten()
    
    length_coord = len(lon)
    length_measure = len(measure)

    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
    
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    fig = go.Figure()

    scatter = go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        text=measure,
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="K"),
            cmin=1000,
            cmax=3000,
            showscale=True
        ),
        mode='markers'
    )

    fig.add_trace(scatter)

    # Update the layout
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="lightgrey",
        ),
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_layout(title="Electron Temperature", template="plotly_white")

    # Show the figure
    st.plotly_chart(fig)

# Main function
def main():
    st.title("Map Drawing and Statistical Analysis Tool")
    draw_map()
    # statistical_analysis()

if __name__ == "__main__":
    main()
