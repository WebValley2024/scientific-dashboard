import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from reduce_frequenct_v2 import reduce_frequency
import xarray as xr
import plotly.express as px
import plotly.io as pio

def plot_xray_count_verse_time(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
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
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
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
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    verse_time = f.VERSE_TIME
    data = f.A413

    log = False
    colormap = 'viridis'

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)

    # Transpose data for correct orientation
    data = data.T
    data = np.log10(data+1)

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=np.arange(data.shape[0]),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/kEV)'),
        #zmin=0,  # np.min(data) if not log else None,
        #zmax=0.5,  # np.max(data) if not log else None,
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='X Energy Spectrum',
        xaxis_title="Verse Time (ms)",
        yaxis_title="Energy (kEV)",
    ))
    return fig


def plot_X_energy_spectrum_utc(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    time = f.UTC_TIME
    data = f.A413

    log = False
    colormap = 'viridis'

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    time = time.values[1:].flatten()

    # Get the length to be able to plot it
    len_time = len(time)
    utctimes = convert_to_utc_time(time)

    # Transpose data for correct orientation
    data = data.T
    data = np.log10(data+1)

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=utctimes,
        y=np.arange(data.shape[0]),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/kEV)'),
        #zmin=0,  # np.min(data) if not log else None,
        #zmax=0.9,  # np.max(data) if not log else None,
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='X Energy Spectrum',
        xaxis_title="Verse Time (ms)",
        yaxis_title="Energy (kEV)",
    ))
    return fig


def heppx_plot(f_path):
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_xray_count_verse_time(f_path))
    with col2:
        st.plotly_chart(plot_xray_count_utc_time(f_path))

    st.plotly_chart(plot_X_energy_spectrum_utc(f_path))


# In your Streamlit app
if __name__ == '__main__':
    st.title("X-Ray Data Visualization")
    file_path = st.text_input("Enter the path to the HDF5 file:", "")
    if file_path:
        heppx_plot(file_path)