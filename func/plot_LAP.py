import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np
from plotting.functions.reducefreq import reduce_frequency
from plotly.subplots import make_subplots


def plot_twin_timeline_verse_time(fig, path):
    # Open the dataset using the h5netcdf engine
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    
    # Extract the required variables
    verse_time = f['VERSE_TIME'][...].values.flatten()
    data = f['A311'][...]
    data2 = f['A321'][...]
    
    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)
    data2 = reduce_frequency(data2, 1)
    
    log = True
    
    # Get the frequency dimension
    try:
        freq = data.shape[1]
    except:
        freq = 1
    
    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[1:].flatten()
    data2 = data2.values[1:].flatten()
    
    # Remove the first element of the verse time and flatten it
    verse_time = verse_time[1:]
    
    # Get the length to be able to plot it
    len_time = len(verse_time)
    
    # Plot everything
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
    
    # Create subplots with a secondary y-axis
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data, name="Electron Density", line=dict(color='blue')),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data2, name="Electron Temperature", line=dict(color='red')),
        secondary_y=True  # y-axis on RHS
    )
    
    # Configure y-axes
    fig.update_yaxes(title_text="1/m^3", secondary_y=False)
    fig.update_yaxes(title_text="K", secondary_y=True)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)
        fig.update_yaxes(type="log", secondary_y=True)
    
    # Configure x-axis
    fig.update_xaxes(title_text="ms")
    
    return fig


def plot_twin_timeline_utc(fig, path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    
    # Extract the required variables
    time = f['UTC_TIME'][...].values.flatten()
    data = f['A311'][...]
    data2 = f['A321'][...]
    
    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)
    data2 = reduce_frequency(data2, 1)
    
    log = True

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
    
    # Remove the first element of the data and flatten it to be able to plot it
    data = data.values[1:].flatten()
    data2 = data2.values[1:].flatten()
    
    # Remove the first element of the time and flatten it
    time = time[1:]
    
    len_time = len(time)
    time_extend = np.concatenate([np.linspace(time[i], time[i+1], freq, endpoint=False) for i in range(len_time - 1)])
    time_extend = np.concatenate([time_extend, np.linspace(time[-2], time[-1], freq)])
    utctimes = convert_to_utc_time(time_extend)
    
    df = pd.DataFrame({
        "data": data,
        "data2": data2,
        "time": utctimes
    })

    # Plotting with Plotly
    fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Electron Density'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['time'], y=df['data2'], mode='lines', name='Electron Temperature', line=dict(color='red')), secondary_y=True)

    # Update y-axes titles
    fig.update_yaxes(title_text="1/m^3", secondary_y=False)
    fig.update_yaxes(title_text="K", secondary_y=True)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)
        fig.update_yaxes(type="log", secondary_y=True)

    # Update x-axis title
    fig.update_xaxes(title_text="Time (UTC)")

    return fig


def plot_on_map_density(fig, path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    
    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    longitude = f['GEO_LON'][...]
    data = f['A311'][...]

    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    try:
        freq = data.shape[1]
    except:
        freq = 1

    measure = data.values[1:].flatten()
    lon = longitude.values[1:].flatten()
    lat = latitude.values[1:].flatten()
    
    length_coord = len(lon)
    length_measure = len(measure)

    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
    
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    scatter = go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        text=measure,
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="1/m^3"),
            cmin=measure.min(),
            cmax=10**11,
            showscale=True
        ),
        mode='markers'
    )

    fig.add_trace(scatter)

    # Update the layout
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="lightgrey",
        ),
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_layout(title="Electron Density", template="plotly_white")

    return fig


def plot_on_map_temperature(fig, path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    
    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    longitude = f['GEO_LON'][...]
    data = f['A321'][...]

    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    try:
        freq = data.shape[1]
    except:
        freq = 1

    measure = data.values[1:].flatten()
    lon = longitude.values[1:].flatten()
    lat = latitude.values[1:].flatten()
    
    length_coord = len(lon)
    length_measure = len(measure)

    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
    
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    scatter = go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        text=measure,
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="K"),
            cmin=1000,
            cmax=3000,
            showscale=True
        ),
        mode='markers'
    )

    fig.add_trace(scatter)

    # Update the layout
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="lightgrey",
        ),
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_layout(title="Electron Temperature", template="plotly_white")

    return fig


def lap_plot(f_path):
    if not f_path:
        return

    # Create a 2x2 grid for plotting
    columns = st.columns(2)
    
    # Plot Electron Temperature and Electron Density on the first row
    with columns[0]:
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        plot_twin_timeline_utc(fig1, f_path)
        st.plotly_chart(fig1)

    with columns[1]:
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        plot_twin_timeline_verse_time(fig2, f_path)
        st.plotly_chart(fig2)

    # Plot Electron Density and Electron Temperature on the second row
    with columns[0]:
        fig3 = go.Figure()
        plot_on_map_density(fig3, f_path)
        st.plotly_chart(fig3)

    with columns[1]:
        fig4 = go.Figure()
        plot_on_map_temperature(fig4, f_path)
        st.plotly_chart(fig4)


# input a list of file paths
 
def aggregated_LAP_electron(files, variable='A311'):
    fig = go.Figure()
 
    for file in files:
        f = xr.open_zarr(file)
 
        # Extract the required variables
        latitude = f['GEO_LAT'][...]
        data = f[variable][...]
 
        # Reduce the frequency of the data
        data = reduce_frequency(data, 1)
 
        # Flatten the data for plotting
        measure = data.values.flatten()
        lat = latitude.values.flatten()

        # Plot the data
        fig.add_trace(
            go.Scatter(x=lat, y=measure, mode='lines', name=str(orbit_number(file)))
        )
 
    # Configure the layout
    if variable == 'A311':
        y_axis_title = "Electron Density (1/m^3)"
    else:
        y_axis_title = "Electron Temperature (K)"
 
    fig.update_layout(
        title=f"{variable} vs GEO_LAT",
        xaxis_title="GEO_LAT",
        yaxis_title=y_axis_title,
        template="plotly_white"
    )

    return fig
 
    # st.plotly_chart(fig)


def orbit_number(filename):
    # Split the filename by underscores
    parts = filename.split('_')
    
    # The desired number is in the 6th position (index 5)
    number = parts[6]
    
    return number
