import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import numpy as np
from plotting.functions.plot_SCM import plot_SCM
from plotting.functions.reducefreq import reduce_frequency

def plot_sequential_SCM(paths):
    # Initialize empty lists to store figures
    all_fig1 = []
    all_fig2 = []
    
    # Loop through each path and plot SCM
    for path in paths:
        try:
            fig1, fig2 = plot_SCM(path, True)
            all_fig1.append(fig1)
            all_fig2.append(fig2)
        except Exception as e:
            st.error(f"Error processing {path}: {str(e)}")
    
    # Create combined figures
    fig_combined1 = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    fig_combined2 = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    
    # Add traces from all individual figures to the combined figures
    for fig1 in all_fig1:
        for trace in fig1.data:
            fig_combined1.add_trace(trace, row=1, col=1)
    
    for fig2 in all_fig2:
        for trace in fig2.data:
            fig_combined2.add_trace(trace, row=1, col=1)
    
    # Update layout
    fig_combined1.update_layout(height=600, title_text="Combined SCM Waveform Plots")
    fig_combined1.update_traces(selector=dict(name='X Waveform'), line=dict(color='red'))
    fig_combined1.update_traces(selector=dict(name='Y Waveform'), line=dict(color='orange'))
    fig_combined1.update_traces(selector=dict(name='Z Waveform'), line=dict(color='green'))
    fig_combined1.update_traces(selector=dict(name='Vector sum'), line=dict(color='blue'))

    fig_combined2.update_layout(height=600, title_text="Combined SCM Angle Plots")
    fig_combined2.update_traces(selector=dict(name='Azimuthal Angle'), line=dict(color='blue'))
    fig_combined2.update_traces(selector=dict(name='Polar Angle'), line=dict(color='green'))

    # Plot using Streamlit
    st.plotly_chart(fig_combined1)
    st.plotly_chart(fig_combined2)

# Example usage
# paths = ["path/to/file1", "path/to/file2", ...]
# plot_sequential_SCM(paths)
