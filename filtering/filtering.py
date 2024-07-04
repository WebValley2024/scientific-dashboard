import glob
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple

import contextily as cx
import geopandas as gpd
import pandas as pd
import streamlit as st
import xarray as xr
from matplotlib import pyplot as plt

from parsing.parsing import extract_dates, extract_orbit
from settings import DATA_DIR
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from tqdm import tqdm

payloads_metadata = gpd.read_file("./filtering/payloads_metadata.gpkg")
ORBIT_GEOMETRY_DF = payloads_metadata.drop_duplicates("semiorbit_nr").drop(
    columns=["file_name"]
)
ORBIT_FILENAME_DF = payloads_metadata[["file_name", "semiorbit_nr", "payload"]]
del payloads_metadata


def semiorbits_payload_filter():
    payload_filtered_files = filtered_files_df[filtered_files_df["payload"] == payload][
        "filepath"
    ]

    ORBIT_FILENAME_DF["payload"] = ORBIT_FILENAME_DF["payload"].str.replace(" ", "_")


def semiorbits_filter(
    start_date: datetime, end_date: datetime, geometry: Tuple[float]
) -> pd.DataFrame:
    """
    Filters the orbits based on the specified date range and geometry.

    Args:
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        geometry (Tuple[float]): The geometry of the area of interest.
    Returns:
        pd.DataFrame: The filtered DataFrame containing the orbits that match the
            specified date range and geometries.
    """
    # if isinstance(geometry, list):
    #     polygons = [Polygon(geometry) for geometry in geometry]
    # else:
    #     polygons = [Polygon(geometry)]
    polygons = [Polygon(geometry)]

    mp = MultiPolygon(polygons)

    # Filter orbits based on date range. We are interested in selecting orbits
    # that overlap with the specified date range.
    matching_orbits = ORBIT_GEOMETRY_DF[
        (ORBIT_GEOMETRY_DF["data_start_time"].dt.date <= end_date)
        & (ORBIT_GEOMETRY_DF["data_end_time"].dt.date >= start_date)
    ]

    # Filter resulting orbits based on geometry, this way it's faster
    matching_orbits = matching_orbits[matching_orbits["geometry"].intersects(mp)]

    return matching_orbits.copy()


def get_filenames_from_orbits(matching_orbits: list):
    # Filter ORBIT_FILENAME_DF based on semiorbit_nr in matching_orbit_values
    filtered_df = ORBIT_FILENAME_DF[
        ORBIT_FILENAME_DF["semiorbit_nr"].isin(matching_orbits)
    ]

    # Select specific columns
    if (
        "file_name" in filtered_df.columns
        and "semiorbit_nr" in filtered_df.columns
        and "payload" in filtered_df.columns
    ):
        filtered_df = filtered_df[["file_name", "semiorbit_nr", "payload"]]
    return filtered_df


def dataset(path):
    try:
        ds = xr.open_zarr(path)
        return ds
    except Exception as e:
        ds = xr.open_dataset(path, engine="h5netcdf", phony_dims="sort")
        return ds


def file_selector():
    folder_path = DATA_DIR
    filenames = os.listdir(folder_path)
    file_paths = [
        os.path.join(folder_path, filename)
        for filename in filenames
        if os.path.isfile(os.path.join(folder_path, filename))
    ]
    return file_paths


# def search_files(st_map, start_date, end_date,):
#     last_active_drawing = st_map.get('last_active_drawing')
#     if last_active_drawing:
#         geometry = last_active_drawing.get('geometry')
#         if geometry and 'coordinates' in geometry:
#             try:
#                 coordinates = geometry['coordinates']
#                 coords = coordinates[0]
#                 intersection_files = date_interval_filter(file_selector(), start_date, end_date)
#                 intersection_files = polygon(coords, intersection_files)
#                 if(intersection_files == []):
#                     return None
#                 else:
#                     return intersection_files
#             except():
#                 st.write("Error in coordinates")
#                 return None
#         else:
#             st.write("No 'coordinates' found in 'geometry'.")
#     else:
#         st.write("No 'last_active_drawing' found in st_map.")

#     return None


def return_coordinates(st_map):
    last_active_drawing = st_map.get("last_active_drawing")
    if last_active_drawing:
        geometry = last_active_drawing.get("geometry")
        if geometry and "coordinates" in geometry:
            try:
                coordinates = geometry["coordinates"]
                coords = coordinates[-1]
                coords = coords[:-1]
                return coords
            except ():
                st.write("Error in coordinates")
                return None
        else:
            st.write("No 'coordinates' found in 'geometry'.")
    else:
        st.write("No 'last_active_drawing' found in st_map.")

    return None


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
    st.write("THE FILE PATHS: ", files_path)
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
    return os.listdir(os.path.join(DATA_DIR, payload))


def payload_filter(file_paths, payload):
    paths = []
    for file_path in file_paths:
        split = file_path.split("/")
        split = split[-1].split("_")
        split = split[2] + "_" + split[3]
        if split == payload:
            paths.append(file_path)

    return paths


def orbit_filter(file_paths, orbit):
    paths = []
    for file_path in file_paths:
        if extract_orbit(file_path) == orbit:
            paths.append(file_path)
    return paths
