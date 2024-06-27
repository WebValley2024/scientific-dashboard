import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

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


filedata = ""

def load_and_display_data(file_path):
    try:
        # Load the dataset using xarray with the h5netcdf engine
        data = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')

        print(file_path)
        # Prepare dataset info
        dataset_info = {
            "Variable": list(data.data_vars),
            "Dimensions": [str(var.dims) for var in data.data_vars.values()],
            "Shape": [var.shape for var in data.data_vars.values()],
            "Data Type": [var.dtype for var in data.data_vars.values()],
        }
        dataset_df = pd.DataFrame(dataset_info)

        # Extract a small subset of the data
        subset = data.isel(phony_dim_0=slice(0, 200))
        
        # Convert subset to DataFrame
        subset_df = subset.to_dataframe()

        # Extract values from the subset for display
        subset_values = subset_df.head(20).to_markdown()

        return dataset_df, subset_df, subset_values, list(subset_df.columns)  # Return columns for dropdown choices
    except Exception as e:
        # Return the error message in case of exception
        return str(e), str(e), "", []