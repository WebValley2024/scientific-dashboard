import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotting.functions.reducefreq import reduce_frequency
import xarray as xr
import plotly.express as px
import plotly.io as pio

def plot_XrayRate_LAT_X(fig, path):
    # Open the dataset using the h5netcdf engine
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')

    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    data = f.XrayRate


    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    log = True

    # Get the frequency dimension
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[1:].flatten()
    # Remove the first element of the latitude and flatten it
    latitude = latitude.values[1:].flatten()

    # Get the length to be able to plot it
    len_lat = len(latitude)

    # Plot everything
    lat_extend = np.concatenate([np.linspace(latitude[i], latitude[i + 1], freq, endpoint=False) for i in range(len_lat - 1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(latitude[-2], latitude[-1], freq)])

    # Create subplots with a secondary y-axis
    fig.add_trace(
        go.Scatter(x=lat_extend, y=data, name="X-Ray Count", line=dict(color='blue')),
        secondary_y=False
    )

    fig.update_yaxes(title_text="1/s", secondary_y=False)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)

    # Configure x-axis
    fig.update_xaxes(title_text="LAT")

    # Configure layout
    fig.update_layout(
        title="X-Ray Count",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )

    return fig




def plot_xray_count_verse_time(path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    verse_time = f.VERSE_TIME
    data = f.XrayRate
    # data = reduce_frequency(data, 1)
    log = False
    # catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[50:].flatten()
    # data2 = data2.values[1:].flatten()

    # do the same with the verse time
    verse_time = verse_time.values[50:].flatten()
    # get the length to be able to plot it
    len_time = len(verse_time)

    # plot everything
    vers_extend = np.concatenate(
        [np.linspace(verse_time[i], verse_time[i + 1], freq, endpoint=False) for i in range(len_time - 1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])

    # Create subplots with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Add trace for the data
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data, name="X-Ray Count", line=dict(color='blue')),
        secondary_y=False
    )

    # Configure y-axes
    fig.update_yaxes(title_text="1/s", secondary_y=False)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)

    # Configure x-axis
    fig.update_xaxes(title_text="ms")

    # Configure layout
    fig.update_layout(
        title="X-Ray Count",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )

    return fig


def plot_xray_count_utc_time(path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    time = f.UTC_TIME
    data = f.XrayRate
    log = False

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[50:].flatten()
    # do the same with the verse time
    time = time.values[50:].flatten()

    len_time = len(time)
    time_extend = np.concatenate(
        [
            np.linspace(time[i], time[i + 1], freq, endpoint=False)
            for i in range(len_time - 1)
        ]
    )
    time_extend = np.concatenate([time_extend, np.linspace(time[-2], time[-1], freq)])
    utctimes = convert_to_utc_time(time_extend)

    df = pd.DataFrame({
        "data": data,
        "time": utctimes
    })

    # Plotting with Plotly
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Counts'), secondary_y=False)

    # Update y-axes titles
    fig.update_yaxes(title_text="1/s", secondary_y=False)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)

    # Update x-axis title
    fig.update_xaxes(title_text="Time (UTC)")

    # Update layout
    fig.update_layout(
        title="X-Ray counts",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600
    )

    return fig


def plot_X_energy_spectrum_verse(path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    verse_time = f.VERSE_TIME
    data = f.A413

    colormap = 'viridis'
    threshold = 1e-10  # Define a threshold for near-zero values

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:].astype(float)  # Ensure data is float type
    verse_time = verse_time.values[1:].flatten()

    # Set near-zero values to NaN
    data[data < threshold] = np.nan

    # Transpose data for correct orientation
    data = data.T

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.Energy_Table_Xray.values.flatten(),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Particles/cm^2/s/kEV')
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='X Energy Spectrum',
        xaxis_title="Verse Time (ms)",
        yaxis_title="Energy (kEV)",
        xaxis=dict(showgrid=False),  # Disable gridlines on x-axis
        yaxis=dict(showgrid=False),  # Disable gridlines on y-axis
    ))
    st.plotly_chart(fig)
def plot_X_energy_spectrum_utc(path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

    time = f.UTC_TIME
    data = f.A413

    colormap = 'viridis'
    threshold = 1e-10  # Define a threshold for near-zero values

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:].astype(float)  # Ensure data is float type
    time = time.values[1:].flatten()

    # Set near-zero values to NaN
    data[data < threshold] = np.nan

    # Apply logarithmic transformation
    #data = np.log10(data+1)

    # Transpose data for correct orientation
    data = data.T

    utctimes = convert_to_utc_time(time)

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=utctimes,
        y=np.arange(data.shape[0]),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Particles/cm^2/s/kEV')
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='X Energy Spectrum',
        xaxis_title="Verse Time (ms)",
        yaxis_title="Energy (kEV)",
        xaxis=dict(showgrid=False),  # Disable gridlines on x-axis
        yaxis=dict(showgrid=False),  # Disable gridlines on y-axis
    ))
    st.plotly_chart(fig)

# not sure if this works
 
def aggregated_HEPPX_xray(files):
 
    fig = go.Figure()
 
    for file in files:
        try:
            f = xr.open_zarr(file)
        except:
            f = xr.open_dataset(file, engine='h5netcdf', phony_dims='sort')
  
        # Extract the required variables
        latitude = f['GEO_LAT'][...]
 
        count_data = f['XrayRate']
 
        # Flatten the data for plotting
        latitude = latitude.values.flatten()
        count_data = count_data.values.flatten()
 
        # Plot the data
        fig.add_trace(
            go.Scatter(x=latitude, y=count_data, mode='lines', name=str(orbit_number(file)))
        )
 
    # Configure the layout
    y_axis_title = "XRay Count"
 
    fig.update_layout(
        title=f"{y_axis_title} vs GEO_LAT",
        xaxis_title="GEO_LAT",
        yaxis_title=y_axis_title,
        template="plotly_white"
    )

    return fig
    # st.plotly_chart(fig)


def heppx_plot(f_path):
    if not f_path:
        return
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_xray_count_verse_time(f_path))
    with col2:
        st.plotly_chart(plot_xray_count_utc_time(f_path))

    st.plotly_chart(plot_X_energy_spectrum_utc(f_path))


def orbit_number(filename):
    # Split the filename by underscores
    parts = filename.split('_')
    
    # The desired number is in the 6th position (index 5)
    number = parts[6]
    
    return number
