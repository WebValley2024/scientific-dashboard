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
from reducefreq import reduce_frequency

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

def plot_EFD(path):
    try:
        f = xr.open_zarr(path)
    except:
        f = xr.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

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
    
    # for axis, spectrum in power_spectra.items():
    #     fig = go.Figure()
    #     fig.add_trace(go.Heatmap(
    #         z=np.log10(spectrum.values.T),  # Apply log10 to intensity (z-axis)
    #         x=verse_time,
    #         y=frequency,
    #         colorscale='Viridis',
    #         colorbar=dict(title='Log Power Spectrum')
    #     ))
    #     fig.update_layout(
    #         title=f"{axis} Power Spectrum",
    #         xaxis_title="Time (ms)",
    #         yaxis_title="Frequency (Hz)",
    #         legend=dict(x=1, y=0.5)
    #     )
        
    #     st.plotly_chart(fig)
 
    # columns = st.columns(len(power_spectra))
    # column_widths = [3, 3]
    # columns = st.columns(column_widths)
    
    # for i, (axis, spectrum) in enumerate(power_spectra.items()):
    #     with columns[i]:
    #         fig = go.Figure()
    #         fig.add_trace(go.Heatmap(
    #             z=np.log10(spectrum.values.T),  # Apply log10 to intensity (z-axis)
    #             x=verse_time,
    #             y=frequency,
    #             colorscale='Viridis',
    #             colorbar=dict(title='Log Power Spectrum')
    #         ))
    #         fig.update_layout(
    #             title=f"{axis} Power Spectrum",
    #             xaxis_title="Time (ms)",
    #             yaxis_title="Frequency (Hz)",
    #             legend=dict(x=1, y=0.5)
    #         )
            
    #         st.plotly_chart(fig)

    columns = st.columns(2)

    for i, (axis, spectrum) in enumerate(power_spectra.items()):
        if i < 2:
            with columns[i]:
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
                st.plotly_chart(fig)

    # Display the third graph in a new row, centered
    if len(power_spectra) > 2:
        empty_col1, centered_col, empty_col2 = st.columns([1, 2, 1])
        with centered_col:
            fig = go.Figure()
            spectrum = list(power_spectra.values())[2]
            axis = list(power_spectra.keys())[2]
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
            st.plotly_chart(fig)

    # Display the first two figures
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1)

    with col2:
        st.plotly_chart(fig2)