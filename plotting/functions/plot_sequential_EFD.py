import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np
from plot_EFD import plot_EFD
paths = []

def plot_sequential_EFD(paths):
        
        
    for i in range(len(paths)):
        try:
            b= xr.open_dataset(paths[i], engine='h5netcdf', phony_dims='sort')
        except:
            c = xr.open_zarr(paths[i])
    fig = make_subplots(rows=len(paths), cols=1, shared_xaxes=True, vertical_spacing=0.1, specs=[[{"secondary_y": True}] for _ in range(len(paths))])
    for i, path in enumerate(paths):
        fig = plot_EFD(path.strip(), fig, i+1)


    fig.update_layout(height=300*len(paths), title_text="Sequential EFD Plots")
    st.plotly_chart(fig)
        
    