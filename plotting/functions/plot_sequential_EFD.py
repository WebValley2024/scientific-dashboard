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
    fig = make_subplots(rows=len(paths), cols=1, shared_xaxes=True, vertical_spacing=0.1, specs=[[{"secondary_y": True}] for _ in range(len(paths))])
    
    for path in enumerate(paths):
        i = plot_EFD(path)
        fig = fig+i
    
    fig.update_layout(height=300*len(paths), title_text="Sequential EFD Plots")
    st.plotly_chart(fig)

plot_sequential_EFD(paths)
