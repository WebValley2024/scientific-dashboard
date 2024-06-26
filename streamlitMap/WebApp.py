
import xarray as xr
import h5py
import pandas as pd
import streamlit as st
import folium
import numpy as np
from streamlit_folium import folium_static
from folium.plugins import Draw


# %%

# Load the H5 file
file_path = '/home/wvuser/scientific-dashboard/streamlitMap/files/CSES_01_LAP_1_L02_A3_174201_20210324_070216_20210324_073942_000.h5'


# %%

# Open the H5 file with xarray using phony_dims='access'
ds = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')


# %%
ds.var()

# %%

indices = np.arange(0, ds.dims['phony_dim_0'], 50)

# Use the isel method with the generated indices to take a subset of the data every 300 records
subset = ds.isel(phony_dim_0=indices)

# Take a subset of the first 18 records from the first dimension across all variables
# subset = ds.isel(phony_dim_0=slice(0, 100))
# subset

# %%
geo_lat = subset.GEO_LAT
geo_lon = subset.GEO_LON

print(geo_lat)
print(geo_lon)

geo_lat_array = subset.GEO_LAT.to_numpy()
geo_lon_array = subset.GEO_LON.to_numpy()

# If you want to combine them into a single array of coordinate pairs
coordinates_array = np.column_stack((geo_lat_array, geo_lon_array))


# %%
st.title("Map Visualization")
map = folium.Map(location=[geo_lat.mean(), geo_lon.mean()], zoom_start=10)

draw = Draw(export=True)

# Step 5: Add the FeatureGroup to the map
map.add_child(draw)

# Create a list of coordinate pa

# Add the coordinates to the map as a PolyLine
folium.PolyLine(coordinates_array, color="blue", weight=2.5, opacity=1).add_to(map)

# Display the map in Streamlit
folium_static(map)


# for lat, lon in zip(geo_lat, geo_lon):
#     folium.Marker([lat, lon]).add_to(map)

# # Use folium_static to render the Folium map in Streamlit
# folium_static(map)


