import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np
from plot_EFD import plot_EFD

paths = [
    "/home/wvuser/cses_personal_data/CSES_01_EFD_1_L02_A1_213330_20211206_164953_20211206_172707_000.h5",
    "/home/wvuser/webvalley2024/Small_samples/CSES_01_EFD_1_L02_A1_104240_20191219_235348_20191220_002832_000.h5",
    "/home/wvuser/webvalley2024/Small_samples/CSES_01_EFD_1_L02_A1_104241_20191220_004117_20191220_011551_000.h5"
]

def plot_sequential_EFD(paths):
    # Initialize empty lists to store figures
    all_fig1 = []
    all_fig2 = []
    
    # Loop through each path and plot EFD
    for path in paths:
        try:
            fig1, fig2 = plot_EFD(path)  # Assuming plot_EFD returns fig1 and fig2
            all_fig1.append(fig1)
            all_fig2.append(fig2)
        except Exception as e:
            st.error(f"Error processing {path}: {str(e)}")
    
    # Concatenate fig1 and fig2 along the x-axis
    fig_combined = make_subplots(rows=1, cols=2, shared_xaxes=True, vertical_spacing=0.1)
    
    for fig1 in all_fig1:
        for trace in fig1.data:
            fig_combined.add_trace(trace, row=1, col=1)
    '''
    for fig2 in all_fig2:
        for trace in fig2.data:
            fig_combined.add_trace(trace, row=2, col=1)
    '''
    # Update layout
    fig_combined.update_layout(height=600, title_text="Combined EFD Plots")
    
    # Plot using Streamlit
    fig_combined.show()

plot_sequential_EFD(paths)