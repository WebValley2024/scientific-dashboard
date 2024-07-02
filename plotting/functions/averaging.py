import xarray as xr
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots







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

    median_array = np.median(stacked, axis=0)
    quartile_25 = np.percentile(stacked, 25, axis=0)
    quartile_75 = np.percentile(stacked, 75, axis=0)
    return [median_array, quartile_25, quartile_75]


"""
takes as input the output of get_med_quantile() and returns a figure containing the median and the quantiles.
the title of the axes and the plot itself are to be added before showing the figure.
"""
def plot_med_quantile(stats):
    median_array = stats[0]
    quartile_25 = stats[1]
    quartile_75 = stats[2]

    
    # Create figure
    fig = go.Figure()

    # Add trace for median
    fig.add_trace(go.Scatter(y=median_array,
                                mode='lines',
                                name='Median'))

    # Add trace for quartiles
    fig.add_trace(go.Scatter(y=quartile_25,
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                                fill='tonexty',
                                name='25th Percentile (1st Quartile)'))

    fig.add_trace(go.Scatter(y=quartile_75,
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                                fill='tonexty',
                                name='75th Percentile (3rd Quartile)'))

    # Update layout
    fig.update_layout(template='plotly_white')

    return fig
