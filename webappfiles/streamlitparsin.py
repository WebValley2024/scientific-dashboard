import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from datetime import datetime
import xarray as xr

# Function to calculate leftmost and rightmost latitude extremes
def calculate_extremes(coordinates):
    if coordinates:
        min_lat = min(point[1] for point in coordinates[0])
        max_lat = max(point[1] for point in coordinates[0])
        return min_lat, max_lat
    return None, None

CSES_DATA_TABLE = {
    'EFD': {'1': 'ULF', '2': 'ELF', '3': 'VLF', '4': 'HF'},
    'HPM': {'1': 'FGM1', '2': 'FGM2', '3': 'CDSM', '5': 'FGM1Hz'},
    'SCM': {'1': 'ULF', '2': 'ELF', '3': 'VLF'},
    'LAP': {'1': '50mm', '2': '10mm'},
    'PAP': {'0': ''},
    'HEP': {'1': 'P_L', '2': 'P_H', '3': 'D', '4': 'P_X'}
}

# Function to parse filename
def parse_filename(filename):
    fl_list = filename[10:].split('_')
    print(fl_list)
    out = {}
    
    if len(filename[10:]) == 66:
        out['Satellite'] = fl_list[0] + fl_list[1]
        out['Instrument'] = fl_list[2]
        
        if fl_list[2] == 'HEP':
            out['Data Product'] = CSES_DATA_TABLE[fl_list[2]][fl_list[3]]
            print(out)
        else:
            out['Data Product'] = 'Unknown'  # Handle other instruments accordingly
            
        out['Instrument No.'] = fl_list[3]
        out['Data Level'] = fl_list[4]
        out['orbitn'] = fl_list[6]
        out['year'] = fl_list[7][0:4]
        out['month'] = fl_list[7][4:6]
        out['day'] = fl_list[7][6:8]
        out['time'] = fl_list[8][0:2] + ':' + fl_list[8][2:4] + ':' + fl_list[8][4:6]
        out['t_start'] = datetime(int(out['year']), int(out['month']), int(out['day']),
                                int(fl_list[8][0:2]), int(fl_list[8][2:4]), int(fl_list[8][4:6]))
        out['t_end'] = datetime(int(fl_list[9][0:4]), int(fl_list[9][4:6]), int(fl_list[9][6:8]),
                                int(fl_list[10][0:2]), int(fl_list[10][2:4]), int(fl_list[10][4:6]))

        print(out)
    elif len(filename[10:]) == 69:
        out['Satellite'] = fl_list[0] + '_01'
        out['Instrument'] = fl_list[1]
        out['Data Product'] = fl_list[2]
        out['Data Level'] = fl_list[-2]
        out['orbitn'] = fl_list[3]
        out['year'] = fl_list[4][0:4]
        out['month'] = fl_list[4][4:6]
        out['day'] = fl_list[4][6:8]
        out['time'] = fl_list[5][0:2] + ':' + fl_list[5][2:4] + ':' + fl_list[5][4:6]
        out['t_start'] = datetime(int(out['year']), int(out['month']), int(out['day']),
                                  int(fl_list[5][0:2]), int(fl_list[5][2:4]), int(fl_list[5][4:6]))
        out['t_end'] = datetime(int(fl_list[6][0:4]), int(fl_list[6][4:6]), int(fl_list[6][6:8]),
                                int(fl_list[7][0:2]), int(fl_list[7][2:4]), int(fl_list[7][4:6]))

    return out


# Initialize Streamlit
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

# Display the map on Streamlit
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
        
        # Parse the filename
        filename = 'CSES_01_HEP_1_L02_A4_176401_20210407_182209_20210407_190029_000.h5'  # Example filename
        parsed_data = parse_filename(filename)
        
        # Display parsed filename details
        st.write("Parsed Filename Details:")
        st.write(parsed_data)
        for key, value in parsed_data.items():
            st.write(f"{key}: {value}")

    else:
        st.write("No 'coordinates' found in 'geometry'.")
else:
    st.write("No 'last_active_drawing' found in st_map.")
