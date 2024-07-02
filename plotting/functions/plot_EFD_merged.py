import streamlit as st
import numpy as np
import plotly.graph_objs as go
import xarray as xr

from plotting.functions.reducefreq import reduce_frequency  # Assuming this import is correct

def plot_EFD(file_paths):
    # Open each dataset
    datasets = [xr.open_zarr(fp) for fp in file_paths]

    # Concatenate datasets along a new dimension
    combined = xr.concat(datasets, dim='phony_dim_0')

    # Extract variables from the combined dataset
    X_Waveform = combined['A111_W'][...]
    Y_Waveform = combined['A112_W'][...]
    Z_Waveform = combined['A113_W'][...]
    verse_time = combined['VERSE_TIME'][...].values.flatten()
    X_Power_spectrum = combined['A111_P'][...]
    Y_Power_spectrum = combined['A112_P'][...]
    Z_Power_spectrum = combined['A113_P'][...]
    latitude = combined['MAG_LAT'][...]
    longitude = combined['MAG_LON'][...]
    frequency = combined['FREQ'][...]
    
    # Calculate derived quantities
    magnitude = np.sqrt(X_Waveform**2 + Y_Waveform**2 + Z_Waveform**2)
    polar_angle = np.degrees(np.arccos(Z_Waveform / magnitude))  # theta
    azimuthal_angle = np.degrees(np.arctan2(Y_Waveform, X_Waveform))  # phi

    # Reduce frequency
    reduced_freq = 100  # Specify the desired frequency here
    X_Waveform = reduce_frequency(X_Waveform, reduced_freq)
    Y_Waveform = reduce_frequency(Y_Waveform, reduced_freq)
    Z_Waveform = reduce_frequency(Z_Waveform, reduced_freq)
    magnitude = reduce_frequency(magnitude, reduced_freq)
    polar_angle = reduce_frequency(polar_angle, reduced_freq)
    azimuthal_angle = reduce_frequency(azimuthal_angle, reduced_freq)

    # Flatten arrays
    X_Waveform = X_Waveform.values.flatten()
    Y_Waveform = Y_Waveform.values.flatten()
    Z_Waveform = Z_Waveform.values.flatten()
    magnitude = magnitude.values.flatten()
    polar_angle = polar_angle.values.flatten()
    azimuthal_angle = azimuthal_angle.values.flatten()

    len_time = len(verse_time)

    # Extend verse_time to match the length of waveforms
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], reduced_freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], reduced_freq)])

    # Plotting with Plotly
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

    # Third figure for power spectra (up to 2 axes in the first row, and the third centered)
    # Third figure for power spectra (up to 2 axes in the first row, and the third centered)
    # Third figure for power spectra (up to 2 axes in the first row, and the third centered)
    columns = st.columns(2)

    # Choose a subset of frequency values to display as ticks
    # Example: Display every 5th frequency value
    tick_frequency = 5
    tick_values = frequency[::tick_frequency]

    for i, (axis, spectrum) in enumerate({'X': X_Power_spectrum, 'Y': Y_Power_spectrum, 'Z': Z_Power_spectrum}.items()):
        if i < 2:
            with columns[i]:
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
                    yaxis=dict(
                        tickmode='array',
                        tickvals=tick_values,  # Specify subset of frequency values
                        ticktext=[str(val) for val in tick_values]  # Optional: Customize tick labels if needed
                    ),
                    legend=dict(x=1, y=0.5)
                )
                st.plotly_chart(fig)

    # Display the third graph in a new row, centered
    if len({'X': X_Power_spectrum, 'Y': Y_Power_spectrum, 'Z': Z_Power_spectrum}) > 2:
        empty_col1, centered_col, empty_col2 = st.columns([1, 2, 1])
        with centered_col:
            fig = go.Figure()
            axis = list({'X': X_Power_spectrum, 'Y': Y_Power_spectrum, 'Z': Z_Power_spectrum}.keys())[2]
            spectrum = list({'X': X_Power_spectrum, 'Y': Y_Power_spectrum, 'Z': Z_Power_spectrum}.values())[2]
            
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
                yaxis=dict(
                    tickmode='array',
                    tickvals=tick_values,  # Specify subset of frequency values
                    ticktext=[str(val) for val in tick_values]  # Optional: Customize tick labels if needed
                ),
                legend=dict(x=1, y=0.5)
            )
            st.plotly_chart(fig)
