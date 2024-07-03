import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np
from plotting.functions.plot_HEPPL import plot_proton_electron_count_verse_time

def plot_sequential_HEPPL(paths):
    # Initialize empty lists to store figures
    all_fig = []
    
    # Loop through each path and plot 
    for path in paths:
        try:
            fig = plot_proton_electron_count_verse_time(path) 
            all_fig.append(fig)
        except Exception as e:
            st.error(f"Error processing {path}: {str(e)}")
    
    # Create a subplot with a row for each figure
    fig_combined = make_subplots(rows=len(all_fig), cols=1, shared_xaxes=True, vertical_spacing=0.05)

    # Add each figure's traces to the combined figure in separate rows
    for i, fig in enumerate(all_fig, start=1):
        for trace in fig.data:
            fig_combined.add_trace(trace, row=i, col=1)
    
    # Update layout
    fig_combined.update_layout(height=600 * len(all_fig), title_text="Combined Proton and Electron Count")
    
    # Update traces for proton and electron counts
    for trace in fig_combined.data:
        if 'Electron Count' in trace.name:
            trace.update(marker=dict(color='red'))
        elif 'Proton Count' in trace.name:
            trace.update(marker=dict(color='blue'))

    # Plot using Streamlit
    st.plotly_chart(fig_combined)

# Example usage
paths = ["path/to/data1.nc", "path/to/data2.nc"]  # Replace with actual paths
plot_sequential_HEPPL(paths)
