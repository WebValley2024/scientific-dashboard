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
    filelist.append(p)
get_med_quantile(filelist, "A311")
"""
def get_med_quantile(filelist, sensor):
    lengths = []
    data = []

    for f in filelist:
        values = f[sensor].values
        data.append(values)
        lengths.append(len(values))
        print(len(values))


    min_length = min(lengths)

    for i in range(len(data)):
        data[i] = data[i][:min_length].flatten()


    stacked = stacked = np.stack(data)

    median_array = np.median(stacked, axis=0)
    quartile_25 = np.percentile(stacked, 25, axis=0)
    quartile_75 = np.percentile(stacked, 75, axis=0)
    return [median_array, quartile_25, quartile_75]

