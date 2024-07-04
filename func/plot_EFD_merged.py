import streamlit as st
import numpy as np
import plotly.graph_objs as go
import xarray as xr
from .reducefreq import reduce_frequency
import os
from plotly.subplots import make_subplots

def plot_EFD(paths):
    if not paths:
        return

    # Initialize subplots with shared x-axis
    fig = make_subplots(rows=len(paths), 
                        subplot_titles=[os.path.basename(path) for path in paths],
                        shared_xaxes=True,
                        vertical_spacing=0.05)

    row = 1  # Start plotting from the first row

    for path in paths:
        f = xr.open_zarr(path)
        X_Waveform = reduce_frequency(f['A111_W'][...], 1).values.flatten()
        Y_Waveform = reduce_frequency(f['A112_W'][...], 1).values.flatten()
        Z_Waveform = reduce_frequency(f['A113_W'][...], 1).values.flatten()
        magnitude = np.sqrt(X_Waveform**2 + Y_Waveform**2 + Z_Waveform**2)
        polar_angle = np.degrees(np.arccos(Z_Waveform / magnitude))
        azimuthal_angle = np.degrees(np.arctan2(Y_Waveform, X_Waveform))

        # Create subplot for waveforms
        fig.add_trace(go.Scatter(x=f['VERSE_TIME'][...].values.flatten(), y=X_Waveform, mode='lines', name='X Waveform'), row=row, col=1)
        fig.add_trace(go.Scatter(x=f['VERSE_TIME'][...].values.flatten(), y=Y_Waveform, mode='lines', name='Y Waveform'), row=row, col=1)
        fig.add_trace(go.Scatter(x=f['VERSE_TIME'][...].values.flatten(), y=Z_Waveform, mode='lines', name='Z Waveform'), row=row, col=1)
        fig.add_trace(go.Scatter(x=f['VERSE_TIME'][...].values.flatten(), y=magnitude, mode='lines', name='Vector sum'), row=row, col=1)

        # Create subplot for power spectra
        # fig.add_trace(go.Heatmap(z=np.log10(f['A111_P'][...].values.T), x=f['VERSE_TIME'][...].values.flatten(), y=f['FREQ'][...].values.flatten(),
        #                          colorscale='Viridis', colorbar=dict(title='Log Power Spectrum')), row=row, col=2)

        # row += 1  # Move to the next row for the next file

    # Update layout for the overall figure
    fig.update_layout(height=len(paths) * 400,  # Adjust height based on the number of files
                      title_text="Waveforms and Power Spectra for Each File",
                      showlegend=False)

    # Set x-axis and y-axis titles for all subplots
    fig.update_xaxes(title_text="Time (ms)", row=len(paths), col=1)
    fig.update_yaxes(title_text="V/m", row=len(paths), col=1)
    fig.update_xaxes(title_text="Time (ms)", row=len(paths), col=2)
    fig.update_yaxes(title_text="Frequency (Hz)", row=len(paths), col=2)

    # Display the plot using Streamlit
    st.plotly_chart(fig)


def parse_filename(filename):
    parts = os.path.basename(filename).split('_')
    for part in parts:
        if part.isdigit() and len(part) == 6:
            return part
    return None
