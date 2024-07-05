import streamlit as st

from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, t
import xarray as xr
import pandas as pd
import os
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from plotting.functions.reducefreq import reduce_frequency

import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import h5py
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from shapely import geometry
from glob import glob
import datetime





def plot_EFD(path, multiple):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
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
            z=np.log10(spectrum.T),  # Apply log10 to intensity (z-axis)
            x=verse_time,
            y=frequency.values.flatten(),
            colorscale='Viridis',
            colorbar=dict(title='Log Power Spectrum')
        ))
        fig.update_layout(
            title=f"{axis} Power Spectrum",
            xaxis_title="Time (ms)",
            yaxis_title="Frequency (Hz)",
            legend=dict(x=1, y=0.5)
        )
        if not multiple:
            st.plotly_chart(fig)
    
    if multiple:
        return fig1, fig2

    # Display the first two figures
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)


def aggregate_EFD_angles(files, angle_type='polar'):

    fig = go.Figure()
 
    for file in files:
        try:
            f = xr.open_zarr(file)
        except:
            f = xr.open_dataset(file, engine='h5netcdf', phony_dims='sort')
 
        # Extract the required variables
        latitude = f['GEO_LAT'][...]
        X_Waveform = f['A111_W'][...]
        Y_Waveform = f['A112_W'][...]
        Z_Waveform = f['A113_W'][...]
 
        # Compute magnitude and angles
        magnitude = np.sqrt(X_Waveform**2 + Y_Waveform**2 + Z_Waveform**2)
        polar_angle = np.degrees(np.arccos(Z_Waveform / magnitude))  # theta
        azimuthal_angle = np.degrees(np.arctan2(Y_Waveform, X_Waveform))  # phi
 
        # Select the angle to plot
        if angle_type == 'polar':
            angle = polar_angle
        elif angle_type == 'azimuth':
            angle = azimuthal_angle
        else:
            raise ValueError("Invalid angle type. Choose 'polar' or 'azimuth'.")
 
        # Reduce the frequency of the data
        latitude = reduce_frequency(latitude, 1)
        angle = reduce_frequency(angle, 1)
 
        # Flatten the data for plotting
        latitude = latitude.values.flatten()
        angle = angle.values.flatten()
 
        # Plot the data
        fig.add_trace(
            go.Scatter(x=latitude, y=angle, mode='lines', name=str(orbit_number(file)))
        )
 
    # Configure the layout
    if angle_type == 'polar':
        y_axis_title = "Polar Angle (degrees)"
    else:
        y_axis_title = "Azimuthal Angle (degrees)"
 
    fig.update_layout(
        title=f"{y_axis_title} vs GEO_LAT",
        xaxis_title="GEO_LAT",
        yaxis_title=y_axis_title,
        template="plotly_white"
    )
    return fig
 
    # st.plotly_chart(fig)

def aggregate_EFD_waveform(files, waveform_type='X'):
    fig = go.Figure()
 
    for file in files:
        try:
            f = xr.open_zarr(file)
        except:
            f = xr.open_dataset(file, engine='h5netcdf', phony_dims='sort')
 
        # Extract the required variables
        latitude = f['GEO_LAT'][...]
 
        if waveform_type == 'X':
            waveform = f['A111_W'][...]
        elif waveform_type == 'Y':
            waveform = f['A112_W'][...]
        elif waveform_type == 'Z':
            waveform = f['A113_W'][...]
        elif waveform_type == 'vector':
            X_Waveform = f['A111_W'][...]
            Y_Waveform = f['A112_W'][...]
            Z_Waveform = f['A113_W'][...]
            waveform = np.sqrt(X_Waveform**2 + Y_Waveform**2 + Z_Waveform**2)
        else:
            raise ValueError("Invalid waveform type. Choose 'X', 'Y', 'Z', or 'vector'.")
 
        # Reduce the frequency of the data
        waveform = reduce_frequency(waveform, 1)
 
        # Flatten the data for plotting
        latitude = latitude.values.flatten()
        waveform = waveform.values.flatten()
 
        # Plot the data
        fig.add_trace(
            go.Scatter(x=latitude, y=waveform, mode='lines', name=str(orbit_number(file)))
        )
 
    # Configure the layout
    y_axis_title = f"{waveform_type} Waveform" if waveform_type != 'vector' else "Vector Magnitude"
 
    fig.update_layout(
        title=f"{y_axis_title} vs GEO_LAT",
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


def plot_A111_W(fig, path):
    # Open the dataset using the h5netcdf engine
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')

    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    data = f['A111_W'][...]


    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    log = True

    # Get the frequency dimension
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[50:].flatten()
    # Remove the first element of the latitude and flatten it
    latitude = latitude.values[50:].flatten()

    # Get the length to be able to plot it
    len_lat = len(latitude)

    # Plot everything
    lat_extend = np.concatenate([np.linspace(latitude[i], latitude[i + 1], freq, endpoint=False) for i in range(len_lat - 1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(latitude[-2], latitude[-1], freq)])

    # Create subplots with a secondary y-axis
    fig.add_trace(
        go.Scatter(x=lat_extend, y=data, name="X-Waveform", line=dict(color='blue')),
        secondary_y=False
    )



    # Configure y-axes
    fig.update_yaxes(title_text="mV/m", secondary_y=False)

    if log:
        fig.update_yaxes(type="log", secondary_y=False)


    # Configure x-axis
    fig.update_xaxes(title_text="Latitude")

    return fig


def plot_A112_W(fig, path):
    # Open the dataset using the h5netcdf engine
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')

    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    data = f['A112_W'][...]


    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    log = True

    # Get the frequency dimension
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[50:].flatten()
    # Remove the first element of the latitude and flatten it
    latitude = latitude.values[50:].flatten()

    # Get the length to be able to plot it
    len_lat = len(latitude)

    # Plot everything
    lat_extend = np.concatenate([np.linspace(latitude[i], latitude[i + 1], freq, endpoint=False) for i in range(len_lat - 1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(latitude[-2], latitude[-1], freq)])

    # Create subplots with a secondary y-axis
    fig.add_trace(
        go.Scatter(x=lat_extend, y=data, name="Y-Waveform", line=dict(color='blue')),
        secondary_y=False
    )
    



    # Configure y-axes
    fig.update_yaxes(title_text="mV/m", secondary_y=False)

    if log:
        fig.update_yaxes(type="log", secondary_y=False)


    # Configure x-axis
    fig.update_xaxes(title_text="Latitude")

    return fig


def plot_A113_W(fig, path):
    # Open the dataset using the h5netcdf engine
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')

    # Extract the required variables
    latitude = f['GEO_LAT'][...]
    data = f['A113_W'][...]
    data_max = data.max()
    data_min = data.min()

    

    # Reduce the frequency of the data
    data = reduce_frequency(data, 1)

    log = True

    # Get the frequency dimension
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[50:].flatten()
    # Remove the first element of the latitude and flatten it
    latitude = latitude.values[50:].flatten()

    # Get the length to be able to plot it
    len_lat = len(latitude)

    # Plot everything
    lat_extend = np.concatenate([np.linspace(latitude[i], latitude[i + 1], freq, endpoint=False) for i in range(len_lat - 1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(latitude[-2], latitude[-1], freq)])

    # Create subplots with a secondary y-axis
    fig.add_trace(
        go.Scatter(x=lat_extend, y=data, name="Z-Waveform", line=dict(color='blue')),
        secondary_y=False
    )
    
    # Configure y-axis
    fig.update_yaxes(title_text="Hz", secondary_y=False, range=[data_min, data_max])
    



    # Configure y-axes
    fig.update_yaxes(title_text="mV/m", secondary_y=False)

    if log:
        fig.update_yaxes(type="log", secondary_y=False)


    # Configure x-axis
    fig.update_xaxes(title_text="Latitude")

    return fig
