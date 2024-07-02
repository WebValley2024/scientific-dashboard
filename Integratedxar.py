import os
from glob import glob
import datetime
import folium
import geopandas as gpd
import h5py
import h5netcdf
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
import logging

from plotting.functions.plot_EFD import plot_EFD
from plotting.functions.plot_LAP import lap_plot
from plotting.functions.plot_HEPPX import heppx_plot
from plotting.functions.plot_SCM import scmplot
from plotting.functions.plot_HEPPH import plotheph

folder_path = '/home/grp2/dhruva-sharma/scientific-dashboard/webappfiles/data/EFD'

def dataset(path):
    try:
        ds = xr.open_zarr(path)
        return ds
    except Exception as e:
        ds = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
        return ds

def variables(data):
    return list(data.keys())

def calculate_extremes(coordinates):
    if coordinates:
        min_lat = min(point[1] for point in coordinates[0])
        max_lat = max(point[1] for point in coordinates[0])
        return min_lat, max_lat
    return None, None

def extract_dates(file_name):
    from datetime import datetime as dt
    try:
        base_name = os.path.basename(file_name)
        parts = base_name.split('_')
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8:
                start_index = i
                break
        if start_index is None:
            raise ValueError(f"Date format not found in file name: {file_name}")
        start_date_str = '_'.join(parts[start_index:start_index + 2])
        end_date_str = '_'.join(parts[start_index + 2:start_index + 4])
        start_date = dt.strptime(start_date_str, '%Y%m%d_%H%M%S').date()
        end_date = dt.strptime(end_date_str, '%Y%m%d_%H%M%S').date()
        return start_date, end_date
    except ValueError as e:
        print(f"Error parsing dates for file {file_name}: {e}")
        return None, None

def date_input():
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start date", datetime.date(2018, 2, 15))
    end_date = col2.date_input("End date", value=datetime.date.today())
    st.write(start_date)
    st.write(end_date)
    return start_date, end_date

def search_files(st_map, start_date, end_date):
    last_active_drawing = st_map.get('last_active_drawing')
    if last_active_drawing:
        geometry = last_active_drawing.get('geometry')
        if geometry and 'coordinates' in geometry:
            coordinates = geometry['coordinates']
            coords = coordinates[0][:-1]
            intersection_files = polygon(coords, file_selector())
            intersection_files = check_Date_interval(intersection_files, start_date, end_date)
            plotting_selector(intersection_files, coordinates)
        else:
            st.write("No 'coordinates' found in 'geometry'.")
    else:
        st.write("No 'last_active_drawing' found in st_map.")

def plotting_selector(intersection_files, coordinates):
    dataset_type = extract_dataset_type(intersection_files)
    option = st.multiselect("Instrument Type", (" ", "EFD", "SCM", "LAP", "HEP_1", "HEP_4", "HEP_2"))
    if st.button("plot"):
        if option:
            for dataset in dataset_type:
                file_path = dataset[0]
                dataset_type = dataset[1]
                for sensors in option:
                    if dataset_type == 'EFD' == sensors:
                        plot_EFD(file_path)
                    elif dataset_type == 'LAP' == sensors:
                        lap_plot(file_path)
                    elif dataset_type == 'HEP_4' == sensors:
                        heppx_plot(file_path)
                    elif dataset_type == 'HEP_1' == sensors:
                        st.write("working on function")
                    elif dataset_type == 'SCM' == sensors:
                        scmplot(file_path)
                    elif dataset_type == 'HEP_2' == sensors:
                        st.write("test")
                        plotheph(file_path)
    min_lat, max_lat = calculate_extremes(coordinates)
    st.write(f"Leftmost Latitude: {min_lat:.6f}")
    st.write(f"Rightmost Latitude: {max_lat:.6f}")

def draw_map():
    m = folium.Map(location=[45.5236, -122.6750], zoom_start=1.15)
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
    start_date, end_date = date_input()
    if "search_files_executed" not in st.session_state:
        st.session_state.search_files_executed = False
    search = st.button("Search Files")
    if search or st.session_state.search_files_executed:
        st.session_state.search_files_executed = True
        search_files(st_map, start_date, end_date)

def polygon(points, files):
    intersectionFile = []
    latitudes = [point[1] for point in points]
    longitudes = [point[0] for point in points]
    lat_min, lat_max = min(latitudes), max(latitudes)
    lon_min, lon_max = min(longitudes), max(longitudes)
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

def file_selector(folder_path='/home/grp2/dhruva-sharma/scientific-dashboard/webappfiles/data/EFD'):
    filenames = os.listdir(folder_path)
    file_paths = [os.path.join(folder_path, filename) for filename in filenames if os.path.isfile(os.path.join(folder_path, filename))]
    return file_paths

def main():
    st.set_page_config(layout="wide")
    st.title("Map Drawing and Statistical Analysis Tool")
    draw_map()

if __name__ == "__main__":
    main()
