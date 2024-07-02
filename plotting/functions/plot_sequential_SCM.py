import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np
from plotting.functions.plot_SCM import plot_SCM
from plotting.functions.reducefreq import reduce_frequency

def plot_sequential_SCM(paths):
    # Initialize empty lists to store figures
    all_fig1 = []
    all_fig2 = []
    
    # Loop through each path and plot EFD
    for path in paths:
        try:
            fig1, fig2 = plot_SCM(path)  # Assuming plot_EFD returns fig1 and fig2
            all_fig1.append(fig1)
            all_fig2.append(fig2)
        except Exception as e:
            st.error(f"Error processing {path}: {str(e)}")
    
    # Concatenate fig1 and fig2 along the x-axis
    fig_combined = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    fig_combined2 = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    for fig1 in all_fig1:
        for trace in fig1.data:
            fig_combined.add_trace(trace, row=1, col=1)
    
    for fig2 in all_fig2:
        for trace in fig2.data:
            fig_combined2.add_trace(trace, row=1, col=1)
    
    # Update layout
    fig_combined.update_layout(height=600, title_text="Combined SCM Plots")
    fig_combined.update_traces(selector=dict(name='X Waveform'), marker=dict(color='red'))
    fig_combined.update_traces(selector=dict(name='Y Waveform'), marker=dict(color='orange'))
    fig_combined.update_traces(selector=dict(name='Z Waveform'), marker=dict(color='green'))



    fig_combined2.update_layout(height=600, title_text="Combined SCM Plots")
    fig_combined2.update_traces(selector=dict(name='Polar Angle'), marker=dict(color='green'))
    # Plot using Streamlit
    st.plotly_chart(fig_combined)
    st.plotly_chart(fig_combined2)

# plot_sequential_SCM(paths)

