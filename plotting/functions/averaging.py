import xarray as xr
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st

"""
gets a list of the files to analyse and the sensor it should analyse as a string. returns as a list:
[median, quantile 25, quantile 75] of the sensor that was selected
example usage:

filelist = []
for p in pathlist:
    f = xr.open_zarr(p)
    filelist.append(f)
get_med_quantile(filelist, "A311")

if multiple sensors from the same files are to be analyzed, open the files only once.
"""
def get_med_quantile(filelist, sensor):
    lengths = []
    data = []

    for f in filelist:
        values = f[sensor].values
        data.append(values)
        lengths.append(len(values))

    

    min_length = min(lengths)

    for i in range(len(data)):
        data[i] = data[i][:min_length].flatten()


    stacked = stacked = np.stack(data)


    median_array = np.nanmedian(stacked, axis=0)
    quartile_25 = np.nanpercentile(stacked, 25, axis=0)
    quartile_75 = np.nanpercentile(stacked, 75, axis=0)
    return [median_array, quartile_25, quartile_75]


"""
takes as input the output of get_med_quantile() and returns a figure containing the median and the quantiles.
the title of the axes and the plot and what is to be displayed on the axes 
have to be added before showing the figure.
"""
def plot_med_quantile(stats, latitude, freq, title_y=""):
    median_array = stats[0]
    quartile_25 = stats[1]
    quartile_75 = stats[2]
 
    length_coord = len(latitude)
    length_measure = len(median_array)
 
    lat_extend = np.concatenate([np.linspace(latitude[i], latitude[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(latitude[-2], latitude[-1], freq)])
 
 
    
    # Create figure
    fig = go.Figure()
 
    # Add trace for median
    fig.add_trace(go.Scatter(y=median_array, x= lat_extend,
                                mode='lines',
                                name='Median'))
 
    # Add trace for quartiles
    fig.add_trace(go.Scatter(y=quartile_25, x= lat_extend,
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                                fill='tonexty',
                                name='25th Percentile (1st Quartile)'))
 
    fig.add_trace(go.Scatter(y=quartile_75, x = lat_extend,
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                                fill='tonexty',
                                name='75th Percentile (3rd Quartile)'))
 
    # Update layout
    fig.update_layout(template='plotly_white')
    fig.update_xaxes(title_text = "Latitude")
    fig.update_yaxes(title_text = title_y)
 
    return fig




"""
takes as input the stats (output of get_med_quantile()) and the figure the stats should get plottet in.
returns the figure with the summarized data as a trace included
example call:

pathlist = ["/home/wvuser/compressed_data/HEPP_H/CSES_01_HEP_2_L02_A4_027321_20180731_233426_20180801_001122_000.zarr.zip","/home/wvuser/compressed_data/HEPP_H/CSES_01_HEP_2_L02_A4_027330_20180801_002138_20180801_005850_000.zarr.zip", "/home/wvuser/compressed_data/HEPP_H/CSES_01_HEP_2_L02_A4_027331_20180801_010906_20180801_014602_000.zarr.zip", "/home/wvuser/compressed_data/HEPP_H/CSES_01_HEP_2_L02_A4_027340_20180801_015626_20180801_023330_000.zarr.zip" ]
filelist = []
for p in pathlist:
    f= xr.open_zarr(p)
    try:
        f=f.rename({"Count_electron":"Count_Electron"})
        f=f.rename({"Count_proton": "Count_Proton"})
    except:
        pass
    filelist.append(f)
stats = get_med_quantile(filelist, "Count_Electron")
fig = plot_proton_electron_count_verse_time("/home/wvuser/compressed_data/HEPP_H/CSES_01_HEP_2_L02_A4_027321_20180731_233426_20180801_001122_000.zarr.zip")
fig = add_stats_trace(stats, fig, "Median Electron Count")
fig
"""
def add_stats_trace(stats, fig, median_name = "Median"):
    median_array = stats[0]
    quartile_25 = stats[1]
    quartile_75 = stats[2]
    x_values = fig.data[0].x
    # Add trace for median
    fig.add_trace(go.Scatter(y=median_array,x=x_values,
                                mode='lines',
                                name=median_name))

    # Add trace for quartiles
    fig.add_trace(go.Scatter(y=quartile_25, x=x_values,
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                                fill='tonexty',
                                name='25th Percentile (1st Quartile)'))

    fig.add_trace(go.Scatter(y=quartile_75, x=x_values,
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                                fill='tonexty',
                                name='75th Percentile (3rd Quartile)'))
    return fig
    