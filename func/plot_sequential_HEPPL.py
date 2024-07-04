import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np
from plotting.functions.plot_HEPPL import plot_proton_electron_count_verse_time 


# def plot_sequential_HEPPL(paths):
#     # Initialize empty lists to store figures
#     all_fig = []
    
#     # Loop through each path and plot 
#     for path in paths:
#         try:
#             fig = plot_proton_electron_count_verse_time(path, True) 
#             all_fig.append(fig)
#         except Exception as e:
#             st.error(f"Error processing {path}: {str(e)}")
    
#     # Concatenate fig1 and fig2 along the x-axis
#     fig_combined = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)
#     fig_combined = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1, specs=[[{"secondary_y": True}]])

#     for fig in all_fig:
#         for trace in fig.data:
#             fig_combined.add_trace(trace, row=1, col=1)
    

    
#     # Update layout
#     fig_combined.update_layout(height=600, title_text="Combined Electron Count")
#     fig_combined.update_traces(selector=dict(name='Electron Count'), marker=dict(color='red'))




#     # Plot using Streamlit
#     st.plotly_chart(fig_combined)


def plot_sequential_HEPPL(paths):
    # Initialize empty lists to store figures
    all_fig = []
    
    # Loop through each path and plot 
    for path in paths:
        try:
            fig = plot_proton_electron_count_verse_time(path, True) 
            all_fig.append(fig)
        except Exception as e:
            st.error(f"Error processing {path}: {str(e)}")
    
    # Create a combined figure with secondary y-axis
    fig_combined = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1, specs=[[{"secondary_y": True}]])

    for fig in all_fig:
        for trace in fig.data:
            # Determine if the trace should go on the secondary y-axis
            secondary_y = True if trace.name == "Proton Count" else False
            fig_combined.add_trace(trace, row=1, col=1, secondary_y=secondary_y)
    
    # Configure y-axes
    fig_combined.update_yaxes(title_text="Electron Count", secondary_y=False)
    fig_combined.update_yaxes(title_text="Proton Count", secondary_y=True)

    # Update layout
    fig_combined.update_layout(
        title_text="Combined Electron and Proton Counts over Time",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )

    # Plot using Streamlit
    return fig_combined
    # st.plotly_chart(fig_combined)
