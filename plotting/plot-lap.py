import xarray as xr
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_twin_timeline_verse_time(data, data2, verse_time, log=True):
    #catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
 
    #remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data=data.values[1:].flatten()
    data2 = data2.values[1:].flatten()
 
    #do the same with the verse time
    verse_time = verse_time.values[1:].flatten()
    #get the length to be able to plot it
    len_time = len(verse_time)
 
    #plot everything
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
 
    # Create subplots with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add trace for the data
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data, name="Electron Density", line=dict(color='blue')),
        secondary_y=False
    )
    fig.add_trace(
    go.Scatter(x=vers_extend, y=data2, name="Electron Temperature", line=dict(color='red')),
    secondary_y=True,  # y-axis on RHS
)

    # Configure y-axes
    fig.update_yaxes(title_text="1/m^3", secondary_y=False)
    fig.update_yaxes(title_text = "K", secondary_y=True)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)
        fig.update_yaxes(type="log", secondary_y=True)


    # Configure x-axis
    fig.update_xaxes(title_text="ms")

    # Configure layout
    fig.update_layout(
        title="Electron Density and Temperature",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )

    # Show the figure
    fig.show()


def plot_twin_timeline_utc(data, data2, time, log=True):

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
    
    # remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[1:].flatten()
    data2 = data2.values[1:].flatten()
    # do the same with the verse time
    time = time.values[1:].flatten()

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
        "data2": data2,
        "time": utctimes
    })

     # Plotting with Plotly
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Electron Density'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['time'], y=df['data2'], mode='lines', name='Electron Temperature', line=dict(color='red')), secondary_y=True)

    # Update y-axes titles
    fig.update_yaxes(title_text="1/m^3", secondary_y=False)
    fig.update_yaxes(title_text="K", secondary_y=True)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)
        fig.update_yaxes(type="log", secondary_y=True)

    # Update x-axis title
    fig.update_xaxes(title_text="Time (UTC)")

    # Update layout
    fig.update_layout(
        title="Electron Temperature and Density",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600
    )

    # Show the figure
    fig.show()





    
