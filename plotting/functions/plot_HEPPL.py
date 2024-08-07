import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# from reducefreq import reduce_frequency
import xarray as xr
import plotly.express as px
import plotly.io as pio
import streamlit as st
from plotting.functions.reducefreq import reduce_frequency


#all these methods take path to a zarr-File!!
#TODO: both plot-against-time-methods do seperate scales for protons and electrons. 
# do we want it that way??

def plot_electron_LAT_L(fig, path):
    f = xr.open_zarr(path)
    verse_time = f.GEO_LAT
    try:
        data2 = f.Count_electron
    except:
        data2 = f.Count_Electron

    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data2 = data2.values[50:].flatten()

    # Do the same with the verse time
    verse_time = verse_time.values[50:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)

    # Plot everything
    # Create extended time array to match the frequency
    freq = data2.shape[0] // len_time  # Assuming data and verse_time have compatible lengths
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])

    # Create subplots with a secondary y-axis
    

    # Add trace for Count_electron (data)


    # Add trace for Count_proton (data2) on the secondary y-axis
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data2, name="Electron Count", line=dict(color='red')),
        secondary_y=False
    )

    # Configure y-axes
    fig.update_yaxes(title_text="Electron Count", secondary_y=False)

    # Configure x-axis
    fig.update_xaxes(title_text="Latitude")

    # Configure layout
    fig.update_layout(
        title="Electron Counts over LAT",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )
    return fig




def plot_proton_LAT_L(fig, path):
    f = xr.open_zarr(path)
    verse_time = f.GEO_LAT
    try:
        data2 = f.Count_proton
    except:
        data2 = f.Count_Proton

    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data2 = data2.values[50:].flatten()

    # Do the same with the verse time
    verse_time = verse_time.values[50:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)

    # Plot everything
    # Create extended time array to match the frequency
    freq = data2.shape[0] // len_time  # Assuming data and verse_time have compatible lengths
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])

    # Create subplots with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Add trace for Count_electron (data)


    # Add trace for Count_proton (data2) on the secondary y-axis
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data2, name="Proton Count", line=dict(color='red')),
        secondary_y=False
    )

    # Configure y-axes
    fig.update_yaxes(title_text="Proton Count", secondary_y=False)

    # Configure x-axis
    fig.update_xaxes(title_text="Latitude")

    # Configure layout
    fig.update_layout(
        title="Proton Counts over LAT",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )

    return fig









def plot_proton_electron_count_verse_time(path, multiple):
    f = xr.open_zarr(path)
    verse_time = f.VERSE_TIME
    try:
        data = f.Count_electron
        data2 = f.Count_proton
    except:
        data = f.Count_Electron
        data2 = f.Count_Proton

    # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[50:].flatten()
    data2 = data2.values[50:].flatten()

    # Do the same with the verse time
    verse_time = verse_time.values[50:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)

    # Plot everything
    # Create extended time array to match the frequency
    freq = data.shape[0] // len_time  # Assuming data and verse_time have compatible lengths
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])

    # Create subplots with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add trace for Count_electron (data)
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data, name="Electron Count", line=dict(color='blue')),
        secondary_y=False
    )

    # Add trace for Count_proton (data2) on the secondary y-axis
    fig.add_trace(
        go.Scatter(x=vers_extend, y=data2, name="Proton Count", line=dict(color='red')),
        secondary_y=True
    )

    # Configure y-axes
    fig.update_yaxes(title_text="Electron Count", secondary_y=False)
    fig.update_yaxes(title_text="Proton Count", secondary_y=True)

    # Configure x-axis
    fig.update_xaxes(title_text="Verse Time (ms)")

    # Configure layout
    fig.update_layout(
        title="Electron and Proton Counts over Time",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600,
    )
    if(not multiple):
        st.plotly_chart(fig)
    return fig

def plot_proton_electron_count_utc(path):

    f = xr.open_zarr(path)
    time = f.UTC_TIME
    try:
        data = f.Count_electron
        data2 = f.Count_proton
    except:
        data = f.Count_Electron
        data2 = f.Count_Proton
    #data = reduce_frequency(data, 1)
    #data2 = reduce_frequency(data2, 1)
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

    fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Electron Count'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['time'], y=df['data2'], mode='lines', name='Proton Count', line=dict(color='red')), secondary_y=True)

    # Update y-axes titles
    fig.update_yaxes(title_text="Electron Counts", secondary_y=False)
    fig.update_yaxes(title_text="Proton Counts", secondary_y=True)
    if log:
        fig.update_yaxes(type="log", secondary_y=False)
        fig.update_yaxes(type="log", secondary_y=True)

    # Update x-axis title
    fig.update_xaxes(title_text="Time (UTC)")

    # Update layout
    fig.update_layout(
        title="Electron and Proton Counts",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600
    )

    st.plotly_chart(fig)

def plot_on_map_electron_count(path):
    f = xr.open_zarr(path)
    latitude = f.GEO_LAT
    longitude = f.GEO_LON
    try:
        data = f.Count_electron
    except:
        data = f.Count_Electron
    #data = reduce_frequency(data, 1)
    try:
        freq = data.shape[1]
    except:
        freq = 1
 
    measure=data.values

    measure = measure[1:].flatten()

 
 
    lon = longitude.values[1:].flatten()
 
    lat = latitude.values[1:].flatten()
    
    length_coord = len(lon)
 
    length_measure = len(measure)
 
 
    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
 
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
 
 
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
 
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    fig = go.Figure()

    scatter = go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        text=measure,
        marker=dict(
            size=10,
            color=measure, #np.log10(measure) if log else measure,
            colorscale='Viridis',
            colorbar=dict(title="Counts"),
            cmin=measure.min(),#np.log10(measure).min() if log else measure.min(),
            cmax=100,#np.log10(measure).max() if log else measure.max(),
            showscale=True
        ),
        mode='markers'
    )

    fig.add_trace(scatter)

    # Update the layout
    fig.update_layout(
        #title="Electron Density",
        geo=dict(
            showland=True,
            landcolor="lightgrey",
        ),
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_layout(title = "Electron Counts", template="plotly_white")

    st.plotly_chart(fig)

def plot_on_map_proton_count(path):
    f = xr.open_zarr(path)
    latitude = f.GEO_LAT
    longitude = f.GEO_LON
    try:
        data = f.Count_proton
    except:
        data = f.Count_Proton
    #data = reduce_frequency(data, 1)
    try:
        freq = data.shape[1]
    except:
        freq = 1
 
    measure=data.values

    measure = measure[1:].flatten()

 
 
    lon = longitude.values[1:].flatten()
 
    lat = latitude.values[1:].flatten()
    
    length_coord = len(lon)
 
    length_measure = len(measure)
 
 
    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
 
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
 
 
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
 
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

    fig = go.Figure()

    scatter = go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        text=measure,
        marker=dict(
            size=10,
            color=measure, #np.log10(measure) if log else measure,
            colorscale='Viridis',
            colorbar=dict(title="Counts"),
            cmin=measure.min(),#np.log10(measure).min() if log else measure.min(),
            cmax=30,#np.log10(measure).max() if log else measure.max(),
            showscale=True
        ),
        mode='markers'
    )

    fig.add_trace(scatter)

    # Update the layout
    fig.update_layout(
        #title="Electron Density",
        geo=dict(
            showland=True,
            landcolor="lightgrey",
        ),
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_layout(title = "Proton Counts", template="plotly_white")

    st.plotly_chart(fig)

def plot_electron_energy_verse(path):
    f = xr.open_zarr(path)
    verse_time = f.VERSE_TIME
    data = f.A411
    data = np.sum(data, axis=2)
    #data = reduce_frequency(data, 1)
    threshold = 1e-10  # Define a threshold for near-zero values

    log = False
    colormap='viridis'

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:].flatten()
    data[data < threshold] = np.nan

    # Get the length to be able to plot it
    len_time = len(verse_time)


    # Transpose data for correct orientation
    data = data.T
    #data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.Energy_Table_Electron.values.flatten(),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Particles/cm^2/s/str'),
        #zmin=0,#np.min(data) if not log else None,
        #zmax=0.8,#np.max(data) if not log else None,
        #zsmooth='best'
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='Electron Energy Spectrum',
        xaxis_title = "Verse Time (ms)",
        yaxis_title = "Energy (KeV)",
        xaxis=dict(showgrid=False),  # Disable gridlines on x-axis
        yaxis=dict(showgrid=False),  # Disable gridlines on y-axis
    ))
    st.plotly_chart(fig)

def plot_electron_energy_utc(path):
    f = xr.open_zarr(path)
    verse_time = f.UTC_TIME
    data = f.A411
    data = np.sum(data, axis=2)
    #data = reduce_frequency(data, 1)
    threshold = 1e-10  # Define a threshold for near-zero values

    log = False
    colormap='viridis'

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:].flatten()
    data[data < threshold] = np.nan

    # Get the length to be able to plot it
    len_time = len(verse_time)

    utctimes = convert_to_utc_time(verse_time)


    # Transpose data for correct orientation
    data = data.T
    #data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=utctimes,
        y=f.Energy_Table_Electron.values.flatten(),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Particles/cm^2/s/str'),
        #zmin=0,#np.min(data) if not log else None,
        #zmax=0.8,#np.max(data) if not log else None,
        #zsmooth='best'
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='Electron Energy Spectrum',
        xaxis_title = "UTC Time",
        yaxis_title = "Energy (KeV)",
        xaxis=dict(showgrid=False),  # Disable gridlines on x-axis
        yaxis=dict(showgrid=False),  # Disable gridlines on y-axis
    ))
    st.plotly_chart(fig)

def plot_electron_pitch_verse(path):
    f = xr.open_zarr(path)
    verse_time = f.VERSE_TIME
    data = f.A411
    data = np.sum(data, axis=1)
    #data = reduce_frequency(data, 1)

    log = False
    colormap='viridis'

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)


    # Transpose data for correct orientation
    data = data.T
    #data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)

    fig = go.Figure()

       # Initialize arrays to hold combined y and z values
    combined_y_values = []
    combined_z_values = []
    cmin = np.min(data)
    cmax = np.max(data)


    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,0][100:],
        z=data[0,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        #zsmooth='best'
    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,1][100:],
        z=data[1,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,2][100:],
        z=data[2,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,3][100:],
        z=data[3,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,4][100:],
        z=data[4,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,5][100:],
        z=data[5,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,6][100:],
        z=data[6,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,7][100:],
        z=data[7,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,8][100:],
        z=data[8,:],
        colorscale=colormap,
        colorbar=dict(title='Particles/cm^2/s/str'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='Electron Pitch Angle',
        xaxis_title = "Verse Time (ms)",
        yaxis_title = "Pitch (degree)",
    ))
    st.plotly_chart(fig)


def plot_proton_energy_verse(path):
    f = xr.open_zarr(path)
    verse_time = f.VERSE_TIME
    data = f.A412
    data = np.sum(data, axis=2)
    #data = reduce_frequency(data, 1)

    log = False
    colormap='viridis'

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)


    # Transpose data for correct orientation
    data = data.T
    data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.Energy_Table_Proton.values.flatten(),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        #zmin=0,#np.min(data) if not log else None,
        #zmax=0.3,#np.max(data) if not log else None,
        #zsmooth='best'
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='Proton Energy Spectrum',
        xaxis_title = "Verse Time (ms)",
        yaxis_title = "Energy (KeV)",
    ))
    st.plotly_chart(fig)

def plot_proton_energy_utc(path):
    f = xr.open_zarr(path)
    verse_time = f.UTC_TIME
    data = f.A412
    data = np.sum(data, axis=2)
    #data = reduce_frequency(data, 1)

    log = False
    colormap='viridis'

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)

    utctimes = convert_to_utc_time(verse_time)


    # Transpose data for correct orientation
    data = data.T
    data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)

    fig = go.Figure()

    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=utctimes,
        y=f.Energy_Table_Proton.values.flatten(),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        #zmin=0,#np.min(data) if not log else None,
        #zmax=0.3,#np.max(data) if not log else None,
        #zsmooth='best'
    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='Proton Energy Spectrum',
        xaxis_title = "UTC Time",
        yaxis_title = "Energy (KeV) CHECK UNIT!",
    ))
    st.plotly_chart(fig)


def plot_proton_pitch_verse(path):
    f = xr.open_zarr(path)
    verse_time = f.VERSE_TIME
    data = f.A412
    data = np.sum(data, axis=1)
    #data = reduce_frequency(data, 1)

    log = False
    colormap='viridis'

    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:].flatten()

    # Get the length to be able to plot it
    len_time = len(verse_time)


    # Transpose data for correct orientation
    data = data.T
    #data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)

    fig = go.Figure()

       # Initialize arrays to hold combined y and z values
    combined_y_values = []
    combined_z_values = []
    cmin = np.min(data)
    cmax = np.max(data)


    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,0][100:],
        z=data[0,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        #zsmooth='best'
    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,1][100:],
        z=data[1,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,2][100:],
        z=data[2,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,3][100:],
        z=data[3,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,4][100:],
        z=data[4,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,5][100:],
        z=data[5,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,6][100:],
        z=data[6,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,7][100:],
        z=data[7,:],
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))
    fig.add_trace(go.Heatmap(
        x=verse_time,
        y=f.PitchAngle.values[:,8][100:],
        z=data[8,:],
        colorscale=colormap,
        colorbar=dict(title='Particles/cm^2/s/str'),
        zmin=cmin,#np.min(data) if not log else None,
        zmax=cmax,#np.max(data) if not log else None,
        showscale=False

    ))

    # Create the layout
    fig.update_layout(go.Layout(
        title='Electron Pitch Angle',
        xaxis_title = "Verse Time (ms)",
        yaxis_title = "Pitch (degree)",
    ))
    st.plotly_chart(fig)


def aggregated_HEPPL_electron_proton(files, count_type='electron'):
 
    fig = go.Figure()
 
    for file in files:
        f = xr.open_zarr(file)
 
        # Extract the required variables
        latitude = f['GEO_LAT'][...]
 
        if count_type == 'electron':
            try:
                count_data = f['Count_electron'][...]
            except:
                count_data = f['Count_Electron'][...]
        else:
            try:
                count_data = f['Count_proton'][...]
            except:
                count_data = f['Count_Proton'][...]
 
        # Flatten the data for plotting
        latitude = latitude.values.flatten()
        count_data = count_data.values.flatten()
 
        # Plot the data
        fig.add_trace(
            go.Scatter(x=latitude, y=count_data, mode='lines', name=str(orbit_number(file)))
        )
 
    # Configure the layout
    if count_type == 'electron':
        y_axis_title = "Electron Count"
    else:
        y_axis_title = "Proton Count"
 
    fig.update_layout(
        title=f"{y_axis_title} vs GEO_LAT",
        xaxis_title="GEO_LAT",
        yaxis_title=y_axis_title,
        template="plotly_white"
    )

    return fig
    # st.plotly_chart(fig)
 

def plot_hepl(path):
    plot_proton_electron_count_verse_time(path, False)
    plot_proton_electron_count_utc(path)
    plot_on_map_electron_count(path)
    plot_on_map_proton_count(path)
    plot_electron_energy_verse(path)
    plot_electron_energy_utc(path)
    plot_electron_pitch_verse(path)
    plot_proton_energy_verse(path)
    plot_proton_energy_utc(path)
    plot_proton_pitch_verse(path)


def orbit_number(filename):
    # Split the filename by underscores
    parts = filename.split('_')
    
    # The desired number is in the 6th position (index 5)
    number = parts[6]
    
    return number
