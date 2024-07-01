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

from efd import plot_EFD
from newlap import lap_plot
from heppx import heppx_plot
from scm import scmplot
from hepph import scmplot

# Replace with your folder path
folder_path = '/home/wvuser/project/data'

def dataset(path):
    return xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')

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

# Function to extract dates from filenames
def extract_dates(file_name):
    from datetime import datetime as dt

    try:
        base_name = os.path.basename(file_name)  # returns the final component of a pathname
        parts = base_name.split('_')

        # find the index of the part that contains the start_date
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8:  # find the part with data format YYYYMMDD
                start_index = i
                break

        if start_index is None:
            raise ValueError(f"Formato data non trovato nel nome del file: {file_name}")

        start_date_str = parts[start_index]
        end_date_str = parts[start_index + 2]

        start_date = dt.strptime(start_date_str, '%Y%m%d').date()
        end_date = dt.strptime(end_date_str, '%Y%m%d').date()

        return start_date, end_date
    except ValueError as e:
        print(f"Errore nel parsing delle date per il file {file_name}: {e}")
        return None, None

# Function for map drawing
def draw_map():
    m = folium.Map(location=[39, 34], zoom_start=1.2)
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
    st_map = st_folium(m, width=1000, height=450)
    # Using Streamlit columns to display widgets side by side
    col1, col2 = st.columns(2)

    # Date input for start date
    start_date = col1.date_input("Start date", datetime.date(2018, 2, 15))
    end_date = col2.date_input("End date", value=datetime.date.today())

    last_active_drawing = st_map.get('last_active_drawing')
    
    if last_active_drawing:
        geometry = last_active_drawing.get('geometry')
        if geometry and 'coordinates' in geometry:
            coordinates = geometry['coordinates']

            coords = geometry['coordinates'][0]  # Access the first inner list
            coords = coords[:-1]

            # Call function and pass coords and file path
            pathskidibidi = polygon(coords, file_selector())

            pathskidibidi = check_Date_interval(pathskidibidi, start_date, end_date)

            dataset_type = extract_dataset_type(pathskidibidi)
            # st.write(dataset_type)
            option = st.multiselect(
                "Instrument Type",
                ("EFD", "SCM", "LAP", "HEP_1", "HEP_2", "HEP_4"))
            # Create a multiselect in Streamlit
            filtered_files = []  # Variable to store the filtered file names based on instrument type


            if option:
                for dataset in dataset_type:
                    file_path = dataset[0]
                    data_type = dataset[1]
                    if data_type in option:
                        filtered_files.append(file_path)


            # st.write("filtered_files")
            # st.write(filtered_files)
            
            # Display the selected file paths
            # if selected_files:
            #     st.write("You selected:")
            #     for file in selected_files:
            #         # Find the full path from the selected file name
            #         full_path = next((info[0] for info in dataset_type if info[0].split('/')[-1] == file), None)
            #         st.write(full_path)
            # else:
            #     st.write("No files selected.")


            # Display the filtered files before the button is pressed
            # st.write("dataset type")
            # st.write(dataset_type)

            # st.write(f"Filtered files before button press: {filtered_files}")

            # filtered_file_names = [os.path.basename(f) for f in filtered_files]
            filtered_files = [[file_path, os.path.basename(file_path)] for file_path in filtered_files]
            # st.write("filtered_files")
            # st.write(filtered_files)
            file_paths = [file_info[0] for file_info in filtered_files]
            file_names = [file_info[1] for file_info in filtered_files]
            selected_file_names = st.multiselect("Select files", options=file_names)
            selected_files = [file_paths[file_names.index(name)] for name in selected_file_names]
            # Use st.multiselect to display file names
            # selected_files = st.multiselect("Select files", options=file_names)
            # st.write(filtered_file_names)
            if st.button("plot"):
                if option:
                    # st.write("Selected options:", option)  # Debug: Print selected options
                    for dataset in selected_file_names:
                        # st.write("Processing dataset:", dataset)  # Debug: Print dataset being processed
                        # Check if any element of option is in dataset
                        if any(opt in dataset for opt in option):
                            # st.write(f"Option {option} matched in dataset {dataset}")  # Debug: Confirm match
                            file_name_test = dataset.split('/')[-1]
                            # st.write("File Name Test:", file_name_test)  # Debug: Print the file name test
                            # Find the full path from the selected file name
                            full_path = next((info[0] for info in filtered_files if info[1] == dataset), None)
                            # st.write("Full Path:", full_path)  # Debug: Print the full path
                            if full_path is not None:
                                if 'EFD' in file_name_test:
                                    # st.write("Plotting EFD:", full_path)
                                    plot_EFD(full_path)
                                elif 'LAP' in file_name_test:
                                    # st.write("Plotting LAP:", full_path)
                                    lap_plot(full_path)
                                elif 'HEP_4' in file_name_test:
                                    # st.write("Plotting HEP_4:", full_path)
                                    heppx_plot(full_path)
                                elif 'HEP_1' in file_name_test:
                                    # st.write("Plotting HEP_1:", full_path)
                                    st.write("Working on function")
                                elif 'HEP_2' in file_name_test:
                                    # st.write("Plotting HEP_1:", full_path)
                                    st.write("Working on function")
                                elif 'SCM' in file_name_test:
                                    # st.write("Plotting SCM:", full_path)
                                    scmplot(full_path)
                            else:
                                st.write("Full path not found for dataset:", dataset)  # Debug: Handle missing full path
                        else:
                            st.write(f"No match for options {option} in dataset {dataset}")  # Debug: Confirm no match


            # Display the filtered files after the button is pressed
            # st.write(f"Filtered files after button press: {filtered_files}")
            
            min_lat, max_lat = calculate_extremes(coordinates)
            st.write(f"Leftmost Latitude: {min_lat:.6f}")
            st.write(f"Rightmost Latitude: {max_lat:.6f}")
        else:
            st.write("No 'coordinates' found in 'geometry'.")
    else:
        st.write("No 'last_active_drawing' found in st_map.")

def polygon(points, files):    
    intersectionFile = []

    latitudes = [point[1] for point in points]
    longitudes = [point[0] for point in points]

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
    return intersectionFile

def check_Date_interval(files_path, start_date_selector, end_date_selector):
    files_list = []
    for file in files_path:
        start_date, end_date = extract_dates(file)
        if start_date and end_date:
            if start_date_selector <= end_date and end_date_selector >= start_date:
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
        else:
            raise ValueError(f"Unknown dataset type in file name: {file_name}")

    return dataset_types

def file_selector(folder_path='/home/wvuser/project/data/'):
    filenames = os.listdir(folder_path)
    file_paths = [os.path.join(folder_path, filename) for filename in filenames]
    return file_paths

# Main function
def main():
    st.set_page_config(layout="wide")
    st.title("Map Drawing and Statistical Analysis Tool")
    draw_map()

if __name__ == "__main__":
    main()
