import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np
from plot_HEPPX import plot_xray_count_utc_time 

paths = ["/home/wvuser/HEPX/._CSES_01_HEP_4_L02_A4_272610_20221231_171527_20221231_175226_000.zarr.zip", "/home/wvuser/HEPX/._CSES_01_HEP_4_L02_A4_272611_20221231_180246_20221231_183954_000.zarr.zip", "/home/wvuser/HEPX/._CSES_01_HEP_4_L02_A4_272611_20221231_182252_20221231_183627_000.zarr.zip", "/home/wvuser/HEPX/._CSES_01_HEP_4_L02_A4_272620_20221231_185010_20221231_192709_000.zarr.zip", "/home/wvuser/HEPX/._CSES_01_HEP_4_L02_A4_272620_20221231_185010_20221231_192709_000.zarr.zip"]

def plot_sequential_HEPPX(paths):
    # Initialize empty lists to store figures
    all_fig = []
    
    # Loop through each path and plot 
    for path in paths:
        try:
            fig = plot_xray_count_utc_time(path) 
            all_fig.append(fig)
        except Exception as e:
            st.error(f"Error processing {path}: {str(e)}")
    
    # Concatenate fig1 and fig2 along the x-axis
    fig_combined = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)

    for fig in all_fig:
        for trace in fig.data:
            fig_combined.add_trace(trace, row=1, col=1)
    

    
    # Update layout
    fig_combined.update_layout(height=600, title_text="Combined Xray Count")
    fig_combined.update_traces(selector=dict(name='Xray Count'), marker=dict(color='red'))




    # Plot using Streamlit
    st.plotly_chart(fig_combined)


plot_sequential_HEPPX(paths)