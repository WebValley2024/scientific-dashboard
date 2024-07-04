import streamlit as st
import xarray as xr
import os 
from parsing2.parsing import extract_dates, extract_orbit
DATA_DIR = "/home/fbk/wv24/LAP"

st.write(DATA_DIR)
def dataset(path):
    try:
        ds = xr.open_zarr(path)
        return ds
    except Exception as e:
        ds = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
        return ds
    

def file_selector():
    folder_path = DATA_DIR
    filenames = os.listdir(folder_path)
    file_paths = [os.path.join(folder_path, filename) for filename in filenames if os.path.isfile(os.path.join(folder_path, filename))]
    return file_paths

def search_files(st_map, start_date, end_date,):
    last_active_drawing = st_map.get('last_active_drawing')
    if last_active_drawing:
        geometry = last_active_drawing.get('geometry')
        if geometry and 'coordinates' in geometry:
            try:
                coordinates = geometry['coordinates']
                coords = coordinates[0]
                coords = wrap_coordinates_list(coords)
                intersection_files = date_interval_filter(file_selector(), start_date, end_date)
                intersection_files = polygon(coords, intersection_files)
                if(intersection_files == []):
                    return None
                else:
                    return intersection_files
            except():
                st.write("Error in coordinates")
                return None
        else:
            st.write("No 'coordinates' found in 'geometry'.")
    else:
        st.write("No 'last_active_drawing' found in st_map.")
    
    return None

def wrap_coordinates_list(coordinate_list):
    """
    Wraps a list of latitude and longitude coordinates to keep them within valid ranges.
    
    Args:
    coordinate_list (list of lists): List containing [latitude, longitude] pairs
    
    Returns:
    list of lists: Wrapped list of [latitude, longitude] pairs
    """
    def wrap_coordinates(lat, lon):
        """
        Wrap latitude and longitude to keep them within their valid ranges.
        
        Latitude range: -90 to 90 degrees
        Longitude range: -180 to 180 degrees
        
        Args:
        lat (float): Latitude value
        lon (float): Longitude value
        
        Returns:
        tuple: Wrapped (latitude, longitude)
        """
        # Wrap latitude
        lat = (lat + 90) % 360 - 90
        if lat > 90:
            lat = 180 - lat
        elif lat < -90:
            lat = -180 - lat

        # Wrap longitude
        lon = (lon + 180) % 360 - 180

        return lat, lon

    return [wrap_coordinates(lat, lon) for lat, lon in coordinate_list]





import pandas as pd

def polygon(points, files):
    intersectionFile = []
    latitudes = [point[1] for point in points]
    longitudes = [point[0] for point in points]
    lat_min, lat_max = min(latitudes), max(latitudes)
    lon_min, lon_max = min(longitudes), max(longitudes)
    for file in files:
        ds = dataset(file)
        try:
            geo_lat = ds.GEO_LAT
            geo_lon = ds.GEO_LON
        except:
            if ds.LonLat.ndim == 3:
                geo_lon = ds.LonLat[0, 0, :]
                geo_lat = ds.LonLat[0, 0, :]
            elif ds.LonLat.ndim == 2:
                geo_lon = ds.LonLat[:, 0]
                geo_lat = ds.LonLat[:, 1]
            else:
                raise ValueError("Unexpected LonLat dimensions")

        lat_mask = (geo_lat >= lat_min) & (geo_lat <= lat_max)
        lon_mask = (geo_lon >= lon_min) & (geo_lon <= lon_max)
        final_mask = lat_mask & lon_mask
        if final_mask.any():
            intersectionFile.append(file)
    return intersectionFile
 

def ascending_descending_filter(files_path, asc_des):
    ascending = []
    descending = []
    # st.write("THE FILE PATHS: ", files_path)
    for file in files_path:
        if int(extract_orbit(file)) % 2 == 0:
            descending.append(file)
        else:
            ascending.append(file)
    if str(asc_des) == "Ascending":
        return ascending
    else:
        return descending
    
def date_interval_filter(files_path, start_date_selector, end_date_selector):
    files_list = []
    for file in files_path:
        start_date, end_date = extract_dates(file)
        if start_date_selector <= end_date and end_date_selector >= start_date:
            files_list.append(file)
    return files_list





def payload_filter2(payload):
    return os.listdir(DATA_DIR + payload)



def payload_filter(file_paths, payload):
    paths = []
    for file_path in file_paths:
        split = file_path.split('/')
        split = split[-1].split('_')
        split = split[2] + '_' + split[3]
        if split == payload:
            paths.append(file_path)
        

    return paths

def orbit_filter(file_paths, orbit):
    paths = []
    for file_path in file_paths:
        if extract_orbit(file_path) == orbit:
            paths.append(file_path)
    return paths