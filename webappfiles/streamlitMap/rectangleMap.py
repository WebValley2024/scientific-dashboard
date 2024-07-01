import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

st.title("Draw Rectangles on Map")

m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Add draw functionality to the map
draw = Draw(
    draw_options={
        'polyline': False,
        'polygon': False,
        'circle': False,
        'marker': False,
        'circlemarker': False,
        'rectangle': True,
    }
)
draw.add_to(m)

st_map = st_folium(m, width=700, height=500)

# Debugging: Print the full st_map object to understand its structure
st.write("st_map object:", st_map)


# Extract the <rectangle coordinates from the map drawing data
if st_map and 'all_drawings' in st_map:
    for drawing in st_map["all_drawings"]:
        if drawing["geometry"]["type"] == "Polygon":
            # Extract the rectangle coordinates
            coordinates = drawing["geometry"]["coordinates"][0]
            st.write("Rectangle Coordinates:", coordinates)
            st.write(coordinates[0][0])
            

