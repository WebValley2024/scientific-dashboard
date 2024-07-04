import os
from glob import glob
import datetime
import folium
import geopandas as gpd
import h5py
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
import xarray as xr
from folium.plugins import Draw
from plotly.subplots import make_subplots
from scipy.stats import skew, kurtosis, t
from shapely import geometry
import streamlit as st
from streamlit_folium import st_folium
from multiprocessing import Pool

import time
from plotting.functions.plot_group1data import plot_group1_data_with_specific_function
from plotting.functions.plot_EFD import plot_EFD
from plotting.functions.plot_EFD import aggregate_EFD_angles
from plotting.functions.plot_EFD import aggregate_EFD_waveform
from plotting.functions.plot_sequential_EFD import plot_sequential_EFD
# from plotting.functions.plot_EFD_merged import plot_EFD

from plotting.functions.plot_LAP import lap_plot
from plotting.functions.plot_LAP import aggregated_LAP_electron
from plotting.functions.LAP_Mul_plot_Final import plot_sequential_LAP

from plotting.functions.plot_SCM import scmplot
from plotting.functions.plot_SCM import aggregated_SCM_angles
from plotting.functions.plot_SCM import aggregated_SCM_waveform
from plotting.functions.plot_sequential_SCM import plot_sequential_SCM

from plotting.functions.plot_HEPPL import plot_hepl
from plotting.functions.plot_sequential_HEPPL import plot_sequential_HEPPL
from plotting.functions.plot_HEPPL import aggregated_HEPPL_electron_proton

from plotting.functions.plot_HEPPH import plotheph
from plotting.functions.plot_HEPPH import aggregated_HEPPH_electron_proton
from plotting.functions.HEPPH_MUL_plot import plot_sequential_HEPPH

from plotting.functions.HEPD_V2_fixed import plot_HEPPD
from plotting.functions.HEPPD_Mul_plot import plot_HEPD_multiple_files
from plotting.functions.plot_HEPPD import plot_HEPD
from plotting.functions.plot_HEPPD import aggregate_HEPPD_electron_proton

from plotting.functions.plot_HEPPX import heppx_plot
from plotting.functions.plot_sequential_HEPPX import plot_sequential_HEPPX
from plotting.functions.plot_HEPPX import aggregated_HEPPX_xray

# from plotting.functions.HEPPL_Mul_plot import plosequential_HEPPL
# from plotting.functions.plot_sequential_HEPPL import plot_proton_electron_count_verse_time


#REPLACE
folder_path = '/home/grp2/dhruva-sharma/scientific-dashboard/webappfiles/data/concat'

def dataset(path):
    try:
        ds = xr.open_zarr(path)
        return ds
    except Exception as e:
        ds = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
        return ds
 
# Function to list all variable names in a dataset
def variables(data):
    return list(data.keys())

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
#         stats_df = pd.DataFrame(stat_values, index=0])
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


def extract_dates(file_name):
    from datetime import datetime as dt

    try:
        base_name = os.path.basename(file_name) #returns the final component of a pathname
        parts = base_name.split('_')
        
        #find the index of the part that contains the start_date
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8:  # find the part with data format YYYYMMDD
                start_index = i
                break
        
        if start_index is None:
            raise ValueError(f"Formato data non trovato nel nome del file: {file_name}")
        
        start_date_str = '_'.join(parts[start_index:start_index + 2]) 
        end_date_str = '_'.join(parts[start_index + 2:start_index + 4])  
        
        start_date = dt.strptime(start_date_str, '%Y%m%d_%H%M%S').date()
        end_date = dt.strptime(end_date_str, '%Y%m%d_%H%M%S').date()
        
        return start_date, end_date
    except ValueError as e:
        print(f"Errore nel parsing delle date per il file {file_name}: {e}")
        return None, None
    
# Function for map drawing
def draw_map():
    # print('asdasdakjsdnas')
    m = folium.Map(location=[45.5236, -122.6750], zoom_start=1.15, continuousWorld=False, noWrap=True)
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
    st_map = st_folium(m, width=1000, height=400)
    # Using Streamlit columns to display widgets side by side
    col1, col2 = st.columns(2)

    # Date input for start date
    start_date = col1.date_input("Start date", datetime.date(2018, 2, 15))
    end_date = col2.date_input("End date", value=datetime.date.today())
    st.write(start_date)
    st.write(end_date)
    # Date input for end date with today's date as default value

    last_active_drawing = st_map.get('last_active_drawing')
    
    if last_active_drawing:
        geometry = last_active_drawing.get('geometry')
        if geometry and 'coordinates' in geometry:
            coordinates = geometry['coordinates']
            # st.write("Coordinates of the last active drawing:")
            # for point in coordinates[0]:  # Assuming it's a polygon and accessing the outer ring
            #     lng, lat = point
            #     st.write(f"Longitude: {lng}, Latitude: {lat}")
            
            coords = geometry['coordinates'][0]  # Access the first inner list
       
            coords = coords[:-1]

            #call function and pass coords and file path
            allfiles = file_selector()
            st.write(allfiles)
            pathskidibidi = check_Date_interval(allfiles,start_date,end_date)

            st.write("dates filtered")
            st.write(pathskidibidi)

            pathskidibidi = polygon(coords, pathskidibidi)


            dataset_type = extract_dataset_type(pathskidibidi)
            print(dataset_type)
            st.write("ajdnajdkansjkdna")
            st.write(dataset_type)

            option = st.multiselect(
                "Instrument Type",
                (" ", "EFD", "SCM", "LAP", "HEP_1", "HEP_4", "HEP_2", "HEP_DDD"))
            
            
            # if st.button("plot"):
            #     if option:
            #         for dataset in dataset_type:
            #             file_path = dataset[0]
            #             dataset_type = dataset[1]
            #             for sensors in option:
            #                 if dataset_type == 'EFD' == sensors:
            #                     plot_EFD(file_path)
            #                 elif dataset_type == 'LAP' == sensors:
            #                     lap_plot(file_path)
            #                 elif dataset_type == 'HEP_4' == sensors:
            #                     heppx_plot(file_path)
            #                 elif dataset_type == 'HEP_1' == sensors:
            #                     st.write("working on function")
            #                 elif dataset_type == 'SCM' == sensors:
            #                     scmplot(file_path)
            #                 elif dataset_type == 'HEP_2' == sensors:
            #                     st.write("test")
            #                     plotheph(file_path)
            # min_lat, max_lat = calculate_extremes(coordinates)
            # st.write(f"Leftmost Latitude: {min_lat:.6f}")
            # st.write(f"Rightmost Latitude: {max_lat:.6f}")
            if st.button("plot"):
                if option:
                    # Initialize arrays for each sensor type
                    efd_files = []
                    lap_files = []
                    hep4_files = []
                    hep1_files = []
                    scm_files = []
                    hep2_files = []
                    hep3_files = []
                    args = []

                    # Populate arrays based on selected datasets and sensors
                    for dataset in dataset_type:
                        file_path = dataset[0]
                        dataset_type = dataset[1]
                        
                        for sensor in option:
                            if dataset_type == 'EFD' and sensor == 'EFD':
                                efd_files.append(file_path)
                            elif dataset_type == 'LAP' and sensor == 'LAP':
                                lap_files.append(file_path)
                            elif dataset_type == 'HEP_4' and sensor == 'HEP_4':
                                hep4_files.append(file_path)
                            elif dataset_type == 'HEP_1' and sensor == 'HEP_1':
                                hep1_files.append(file_path)
                            elif dataset_type == 'SCM' and sensor == 'SCM':
                                scm_files.append(file_path)
                            elif dataset_type == 'HEP_2' and sensor == 'HEP_2':
                                hep2_files.append(file_path)
                            elif dataset_type == 'HEP_DDD' and sensor == 'HEP_DDD':
                                hep3_files.append(file_path)

                        

                    if(len(scm_files) > 1):
                        for i in range(3):
                            args.append((scm_files, 'SCM', i))
                        # plot_sequential_SCM(scm_files)
                        # aggregated_SCM_angles(scm_files)
                        # aggregated_SCM_waveform(scm_files)
                    elif(len(scm_files)==1):
                        args.append((scm_files, 'SCM_s', 0))
                        # scmplot(scm_files)


                    if(len(efd_files) > 1):
                        plot_group1_data_with_specific_function("earthquake", efd_files, "EFD")
                        for i in range(3):
                            args.append((efd_files, 'EFD', i))
                        # paralleltest(efd_files)
                        # plot_sequential_EFD(efd_files)
                        # aggregate_EFD_angles(efd_files)
                        # aggregate_EFD_waveform(efd_files)
                    elif(len(efd_files)==1):
                        args.append((efd_files[0], 'EFD_s', 0))

                        # plot_EFD(efd_files, False)



                    if(len(lap_files) > 1):
                        for i in range(2):
                            args.append((lap_files, 'LAP', i))
                        # plot_sequential_LAP(lap_files)
                        # aggregated_LAP_electron(lap_files)
                    elif(len(lap_files)==1):
                        args.append((lap_files[0], 'LAP_s', 0))
                        # lap_plot(lap_files[0])




                    if(len(hep1_files) > 1):
                        for i in range(2):
                            args.append((hep1_files, 'HEPL', i))
                        # plot_proton_electron_count_verse_time(hep1_files[0], False)
                        # plot_sequential_HEPPL(hep1_files)
                        # aggregated_HEPPL_electron_proton(hep1_files)
                    elif(len(hep1_files)==1):
                        args.append((hep1_files[0], 'HEPL_s', 0))
                        # plot_hepl(hep1_files, False)




                    if(len(hep2_files) > 1):
                        for i in range(2):
                            args.append((hep2_files, 'HEPH', i))
                        # plot_sequential_HEPPH(hep2_files)
                        # aggregated_HEPPH_electron_proton(hep2_files)
                    elif(len(hep2_files)==1):
                        args.append((hep2_files[0], 'HEPH_s', 0))
                        # plotheph(hep2_files[0])



                    #FIX HEP_DDD (john)
                    if(len(hep3_files) > 1):
                        for i in range(2):
                            args.append((hep3_files, 'HEPD', i))
                        # plot_HEPD_multiple_files(hep3_files)
                        # aggregate_HEPPD_electron_proton(hep3_files)
                    elif(len(hep3_files)==1):
                        args.append((hep3_files[0], 'HEPD', 0))
                        # plot_HEPD(hep3_files[0])



                    if(len(hep4_files) > 1):
                        for i in range(2):
                            args.append((hep4_files, 'HEPX', i))
                        # plot_sequential_HEPPX(hep4_files)
                        # aggregated_HEPPX_xray(hep4_files)
                        # plot_HEPD_multiple_files(hep3_files)
                    elif(len(hep4_files)==1):
                        args.append((hep4_files[0], 'HEPX', 0))
                        # heppx_plot(hep4_files[0])

                st.write(time.time())
                with Pool(8) as p:
                    for fig in p.starmap(paralleltest, args):
                        st.write(time.time())
                        if isinstance(fig, tuple):
                            st.write(time.time())
                            for f in fig:
                                st.plotly_chart(f)
                        else:
                            st.plotly_chart(fig)
                st.write(time.time())
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
        try:
            geo_lat = ds.GEO_LAT
            geo_lon = ds.GEO_LON
        except:
            LonLat = ds.LonLat
            if LonLat.ndim == 3:
                geo_lon = LonLat[0, 0, :]
                geo_lat = LonLat[0, 0, :]
            elif LonLat.ndim == 2:
                geo_lon = LonLat[:, 0]
                geo_lat = LonLat[:, 1]
        lat_mask = (geo_lat >= lat_min) & (geo_lat <= lat_max)
        lon_mask = (geo_lon >= lon_min) & (geo_lon <= lon_max)
 
        final_mask = lat_mask & lon_mask

 
        if final_mask.any():
            intersectionFile.append(file)
    return intersectionFile
 

def check_Date_interval(files_path, start_date_selector, end_date_selector):
    files_list = []
    for file in files_path:
        print(file)
        start_date, end_date = extract_dates(file)
        if(start_date_selector <= end_date and end_date_selector >= start_date):
            files_list.append(file)

    return files_list


def extract_dataset_type(file_paths):    
    dataset_types = []
    
    for file_path in file_paths:
        file_name = file_path.split('/')[-1]
        
        if 'EFD' in file_name:
            dataset_types.append([file_path, 'EFD'])
        elif 'LAP' in file_name:
            dataset_types.append([file_path, 'LAP'])
        elif 'SCM' in file_name:
            dataset_types.append([file_path, 'SCM'])
        elif 'HEP_4' in file_name:
            dataset_types.append([file_path, 'HEP_4'])
        elif 'HEP_1' in file_name:
            dataset_types.append([file_path, 'HEP_1'])
        elif 'HEP_2' in file_name:
            dataset_types.append([file_path, 'HEP_2'])
        elif 'HEP_DDD' in file_name:
            dataset_types.append([file_path, 'HEP_DDD'])
        else:
            raise ValueError(f"Unknown dataset type in file name: {file_name}")
    return dataset_types

def file_selector(folder_path = '/home/grp2/dhruva-sharma/scientific-dashboard/webappfiles/data/concat'):
    filenames = os.listdir(folder_path)
    file_paths = [os.path.join(folder_path, filename) for filename in filenames]
    st.write("files selected")
    return file_paths

def paralleltest(file_path, sensor, i):
    if sensor == 'EFD':
        st.write("efd")
        if(i == 0):
            return aggregate_EFD_angles(file_path)
        elif(i == 1):
            return aggregate_EFD_waveform(file_path)
        elif(i == 2):
            return plot_sequential_EFD(file_path)
    elif sensor == "SCM":
        st.write("scm")
        if(i == 0):
            return plot_sequential_SCM(file_path)
        elif(i == 1):
            return aggregated_SCM_angles(file_path)
        elif(i == 2):
            return aggregated_SCM_waveform(file_path)
    elif sensor == "LAP":
        st.write("scm")
        if(i == 0):
            return plot_sequential_LAP(file_path)
        elif(i == 1):
            return aggregated_LAP_electron(file_path)
    elif sensor == "HEPL":
        st.write("hepl")
        if(i == 0):
            return plot_sequential_HEPPL(file_path)
        elif(i == 1):
            return aggregated_HEPPL_electron_proton(file_path)
    elif sensor == "HEPH":
        st.write("heph")
        if(i == 0):
            return plot_sequential_HEPPH(file_path)
        elif(i == 1):
            return aggregated_HEPPH_electron_proton(file_path)
    elif sensor == "HEPD":
        st.write("hepd")
        if(i == 0):
            return plot_HEPD_multiple_files(file_path)
        elif(i == 1):
            return aggregate_HEPPD_electron_proton(file_path)
    elif sensor == "HEPX":
        if(i == 0):
            return plot_sequential_HEPPX(file_path)
        elif(i == 1):
            return aggregated_HEPPX_xray(file_path)
                
# Main function 
def main():
    st.title("Map Drawing and Statistical Analysis Tool")
    draw_map()
    # statistical_analysis()



if __name__ == "__main__":
    main()
    
