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
    
    # Concatenate fig1 and fig2 along the x-axis
    fig_combined = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)

    for fig in all_fig:
        for trace in fig.data:
            fig_combined.add_trace(trace, row=1, col=1)
    

    
    # Update layout
    fig_combined.update_layout(height=600, title_text="Combined Electron Count")
    fig_combined.update_traces(selector=dict(name='Electron Count'), marker=dict(color='red'))




    # Plot using Streamlit
    st.plotly_chart(fig_combined)


