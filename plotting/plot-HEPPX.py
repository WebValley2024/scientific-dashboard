import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from reducefreq import reduce_frequency
import xarray as xr

def plot_xray_count_verse_time(path):
    f = xr.open_dataset(path)
    verse_time = f.VERSE_TIME
    data = f.XrayRate
    #data = reduce_frequency(data, 1)
    log = False
    #catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
 
    #remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data=data.values[50:].flatten()
    #data2 = data2.values[1:].flatten()
 
    #do the same with the verse time
    verse_time = verse_time.values[50:].flatten()
    #get the length to be able to plot it
    len_time = len(verse_time)
 
    #plot everything
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
 
    # Create subplots with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Add trace for the data
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data, name="X-Ray Count", line=dict(color='blue')),
        secondary_y=False
    )

    # Configure y-axes
    fig.update_yaxes(title_text="1/s", secondary_y=False)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)


    # Configure x-axis
    fig.update_xaxes(title_text="ms")

    # Configure layout
    fig.update_layout(
        title="X-Ray Count",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )

    # Show the figure
    fig.show()


def plot_xray_count_utc_time(path):

    f = xr.open_dataset(path)
    time = f.UTC_TIME
    data = f.XrayRate
    log = False

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
    
    # remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[50:].flatten()
    # do the same with the verse time
    time = time.values[50:].flatten()

    len_time = len(time)
    time_extend = np.concatenate(
        [
            np.linspace(time[i], time[i + 1], freq, endpoint=False)
            for i in range(len_time - 1)
        ]
    )
    time_extend = np.concatenate([time_extend, np.linspace(time[-2], time[-1], freq)])
    utctimes = convert_to_utc_time(time_extend)


    df = pd.DataFrame({
        "data": data,
        "time": utctimes
    })

     # Plotting with Plotly
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Counts'), secondary_y=False)
    
    # Update y-axes titles
    fig.update_yaxes(title_text="1/s", secondary_y=False)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)

    # Update x-axis title
    fig.update_xaxes(title_text="Time (UTC)")

    # Update layout
    fig.update_layout(
        title="X-Ray counts",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600
    )

    # Show the figure
    fig.show()