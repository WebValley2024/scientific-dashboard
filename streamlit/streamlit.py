import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from datetime import datetime, timezone
import xarray as xr

# Function to calculate leftmost and rightmost latitude extremes
def calculate_extremes(coordinates):
    if coordinates:
        min_lat = min(point[1] for point in coordinates[0])
        max_lat = max(point[1] for point in coordinates[0])
        return min_lat, max_lat
    return None, None

st.title("Draw Rectangles on Map")

# Initialize a map centered at a specific latitude and longitude
m = folium.Map(location=[45.5236, -122.6750], zoom_start=1.5)


# Add draw functionality to the map
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

# Display the map
st_map = st_folium(m, width=700, height=500)

# Get the last active drawing from st_map
last_active_drawing = st_map.get('last_active_drawing')

if last_active_drawing is not None:
    geometry = last_active_drawing.get('geometry')
    if geometry is not None and 'coordinates' in geometry:
        coordinates = geometry['coordinates']
        st.write("Coordinates of the last active drawing:")
        for point in coordinates[0]:  # Assuming it's a polygon and accessing the outer ring
            lng, lat = point
            st.write(f"Longitude: {lng}, Latitude: {lat}")
        
        # Calculate extremes
        min_lat, max_lat = calculate_extremes(coordinates)
        st.write(f"Leftmost Latitude: {min_lat:.6f}")
        st.write(f"Rightmost Latitude: {max_lat:.6f}")
    else:
        st.write("No 'coordinates' found in 'geometry'.")
else:
    st.write("No 'last_active_drawing' found in st_map.")
