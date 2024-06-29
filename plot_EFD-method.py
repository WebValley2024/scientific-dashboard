import geopandas as gpd
import xarray as xr
import numpy as np
import plotly.graph_objs as go
import geopandas as gpd


def plot_EFD_on_map(data, latitude, longitude):
    
    try:
        freq = data.shape[1]
    except IndexError:
        freq = 1

    measure = data.values.flatten()

    lon = longitude.values.flatten()
    lat = latitude.values.flatten()

    length_coord = len(lon)
    length_measure = len(measure)

    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])

    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    # Create a scatter plot on a map using Plotly
    fig = go.Figure()

    # Load world map using geopandas
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Plot world map as background
    fig.add_trace(go.Choropleth(
        geojson=world.__geo_interface__,
        locations=world.index,
        z=np.zeros(len(world)),  # Dummy values for Choropleth trace
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        hoverinfo='none',
        showscale=False
    ))

    # Scatter plot for data points
    fig.add_trace(go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        mode='markers',
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="V/m"),
            opacity=0.8,
            colorbar_thickness=20,
            colorbar_x=0.85,
            colorbar_y=0.5,
            colorbar_bgcolor='rgba(255,255,255,0.5)'
        ),
        name="Field magnitude"
    ))

    fig.update_geos(
        projection_type="natural earth",
        landcolor="lightgrey",
        oceancolor="lightblue",
        showland=True,
        showocean=True,
        showcountries=True,
        showcoastlines=True,
        showframe=False,
        coastlinewidth=0.5,
        coastlinecolor="white"
    )

    fig.update_layout(
        title="Electric field magnitude during the orbit",
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth'
        ),
        geo_scope='world',
        height=600,
        margin={"r":0,"t":30,"l":0,"b":0},
        showlegend=False
    )

    fig.show()


def reduce_frequency(data_array, frequency):
    """
    Reduce the number of measurements in each row of the xarray based on the specified frequency,
    while preserving the metadata.
    Parameters:
    data_array (xarray.DataArray): The input xarray.
    frequency (int): The number of elements to keep in each row.
    Returns:
    xarray.DataArray: The reduced xarray.
    """
    num_rows, num_cols = data_array.shape
    if frequency > num_cols:
        raise ValueError("Frequency cannot be greater than the number of columns in the data array.")
    reduced_rows = []
    for row in data_array.values:
        indices = np.linspace(0, num_cols - 1, frequency, dtype=int)
        reduced_row = row[indices]
        reduced_rows.append(reduced_row)
    reduced_values = np.stack(reduced_rows, axis=0)
    reduced_data_array = xr.DataArray(reduced_values,
                                      dims=[data_array.dims[0], 'reduced_freq'],
                                      coords={data_array.dims[0]: data_array.coords[data_array.dims[0]],
                                              'reduced_freq': indices},
                                      attrs=data_array.attrs)
    return reduced_data_array
 

 
def plot_EFD(path):
    f = xr.open_dataset(path, phony_dims='sort')
    print(f)
    X_Waveform = f['A111_W'][...]
    Y_Waveform = f['A112_W'][...]
    Z_Waveform = f['A113_W'][...]
    verse_time = f['VERSE_TIME'][...].values.flatten()
    X_Power_spectrum = f['A111_P'][...]
    Y_Power_spectrum = f['A112_P'][...]
    Z_Power_spectrum = f['A113_P'][...]
    latitude = f['MAG_LAT'][...]
    longitude = f['MAG_LON'][...]
    frequency = f['FREQ'][...]
    magnitude = np.sqrt(X_Waveform**2 + Y_Waveform**2 + Z_Waveform**2)
    polar_angle = np.arccos(Z_Waveform / magnitude)  # theta
    azimuthal_angle = np.arctan2(Y_Waveform, X_Waveform)  # phi
 
    # Convert angles to degrees
    polar_angle = np.degrees(polar_angle)
    azimuthal_angle = np.degrees(azimuthal_angle)
 
    reduced_freq = 100  # Specify the desired frequency here
    X_Waveform = reduce_frequency(X_Waveform, reduced_freq)
    Y_Waveform = reduce_frequency(Y_Waveform, reduced_freq)
    Z_Waveform = reduce_frequency(Z_Waveform, reduced_freq)
    magnitude = reduce_frequency(magnitude, reduced_freq)
    polar_angle = reduce_frequency(polar_angle, reduced_freq)
    azimuthal_angle = reduce_frequency(azimuthal_angle, reduced_freq)
 
    X_Waveform = X_Waveform.values.flatten()
    Y_Waveform = Y_Waveform.values.flatten()
    Z_Waveform = Z_Waveform.values.flatten()
    magnitude = magnitude.values.flatten()
    polar_angle = polar_angle.values.flatten()
    azimuthal_angle = azimuthal_angle.values.flatten()
 
    len_time = len(verse_time)
 
    # Ensure vers_extend has the same length as the waveforms
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], reduced_freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], reduced_freq)])
    # First figure for waveforms and magnitude
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=vers_extend, y=X_Waveform, mode='lines', name='X Waveform'))
    fig1.add_trace(go.Scatter(x=vers_extend, y=Y_Waveform, mode='lines', name='Y Waveform'))
    fig1.add_trace(go.Scatter(x=vers_extend, y=Z_Waveform, mode='lines', name='Z Waveform'))
    fig1.add_trace(go.Scatter(x=vers_extend, y=magnitude, mode='lines', name='Vector sum'))
 
    fig1.update_layout(
        title="X, Y, Z Waveforms and the Vector Sum",
        xaxis_title="Time (ms)",
        yaxis_title="V/m",
        legend=dict(x=1, y=0.5)
    )
 
    # Second figure for polar and azimuthal angles
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=vers_extend, y=polar_angle, mode='lines', name='Polar Angle', yaxis='y2'))
    fig2.add_trace(go.Scatter(x=vers_extend, y=azimuthal_angle, mode='lines', name='Azimuthal Angle', yaxis='y3'))
 
    fig2.update_layout(
        title="Polar and Azimuthal Angles",
        xaxis_title="Time (ms)",
        yaxis2=dict(
            title="Polar Angle (degrees)",
            range=[0, 180],
            side='left'
        ),
        yaxis3=dict(
            title="Azimuthal Angle (degrees)",
            range=[0, 360],
            overlaying='y2',
            side='right'
        ),
        legend=dict(x=1.08, y=0.54)
    )
 
    # Third figure for power spectra
    power_spectra = {'X': X_Power_spectrum, 'Y': Y_Power_spectrum, 'Z': Z_Power_spectrum}
    for axis, spectrum in power_spectra.items():
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=np.log10(spectrum.values.T),  # Apply log10 to intensity (z-axis)
            x=verse_time,
            y=frequency,
            colorscale='Viridis',
            colorbar=dict(title='Log Power Spectrum')
        ))
        fig.update_layout(
            title=f"{axis} Power Spectrum",
            xaxis_title="Time (ms)",
            yaxis_title="Frequency (Hz)",
            legend=dict(x=1, y=0.5)
        )
        fig.show()
 
    # Display the first two figures
    fig1.show()
    fig2.show()
    plot_EFD_on_map(magnitude, latitude, longitude)




def plot_EFD_on_map(data, latitude, longitude):
    
    try:
        freq = data.shape[1]
    except IndexError:
        freq = 1

    measure = data.values.flatten()

    lon = longitude.values.flatten()
    lat = latitude.values.flatten()

    length_coord = len(lon)
    length_measure = len(measure)

    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])

    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    # Create a scatter plot on a map using Plotly
    fig = go.Figure()

    # Load world map using geopandas
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Plot world map as background
    fig.add_trace(go.Choropleth(
        geojson=world.__geo_interface__,
        locations=world.index,
        z=np.zeros(len(world)),  # Dummy values for Choropleth trace
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        hoverinfo='none',
        showscale=False
    ))

    # Scatter plot for data points
    fig.add_trace(go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        mode='markers',
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="V/m"),
            opacity=0.8,
            colorbar_thickness=20,
            colorbar_x=0.85,
            colorbar_y=0.5,
            colorbar_bgcolor='rgba(255,255,255,0.5)'
        ),
        name="Field magnitude"
    ))

    fig.update_geos(
        projection_type="natural earth",
        landcolor="lightgrey",
        oceancolor="lightblue",
        showland=True,
        showocean=True,
        showcountries=True,
        showcoastlines=True,
        showframe=False,
        coastlinewidth=0.5,
        coastlinecolor="white"
    )

    fig.update_layout(
        title="Electric field magnitude during the orbit",
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth'
        ),
        geo_scope='world',
        height=600,
        margin={"r":0,"t":30,"l":0,"b":0},
        showlegend=False
    )

    fig.show()


path = "/home/wvuser/webvalley2024/Small_samples/CSES_01_EFD_1_L02_A1_104240_20191219_235348_20191220_002832_000.h5"


f = xr.open_dataset(path, phony_dims='sort')

latitude = f['MAG_LAT'][...]
longitude = f['MAG_LON'][...]
X_Waveform = f['A111_W'][...]
Y_Waveform = f['A112_W'][...]
Z_Waveform = f['A113_W'][...]
magnitude=  np.sqrt(X_Waveform**2 + Y_Waveform**2 + Z_Waveform**2)
plot_EFD_on_map(magnitude, latitude, longitude)
plot_EFD(path)