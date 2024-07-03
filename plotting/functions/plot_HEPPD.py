import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .reducefreq import reduce_frequency
import xarray as xr
import plotly.express as px
import plotly.io as pio
import geopandas as gpd
 
def plot_proton_electron_count_utc(path):
    if not path:
        return
    f = xr.open_zarr(path)
 
    time = f.UTCTime
    try:
        data = f.HEPD_ele_counts
        data2 = f.HEPD_pro_counts
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
 

def plot_electron_energy_utc(path):
    f = xr.open_zarr(path)
    verse_time = f.UTCTime
    data = f.HEPD_ele_energy_pitch
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
    data[data == 0] = np.nan
 
 
    # Transpose data for correct orientation
    data = data.T
    data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)
 
    fig = go.Figure()
    #fig.update_yaxes(title_text="Electron Energy", secondary_y=False)
    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=utctimes,
        y=f.HEPD_ele_energy_table.values.flatten(),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        #zmin=0,#np.min(data) if not log else None,
        #zmax=0.8,#np.max(data) if not log else None,
        #zsmooth='best'
    ))
    fig.update_layout(
        title="Electron Energy over UTC Time",
        xaxis_title="UTC Time",
        yaxis_title=f"{f.HEPD_ele_energy_table.Units}",
        yaxis=dict(type='log', title='Electron Energy (MeV)')
    )
    st.plotly_chart(fig)
#f = xr.open_dataset(path, phony_dims='sort')
#f
 

def plot_proton_energy_utc(path):
    f = xr.open_zarr(path)
    verse_time = f.UTCTime
    data = f.HEPD_pro_energy_pitch
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
    data[data == 0] = np.nan
 
 
    # Transpose data for correct orientation
    data = data.T
    data = np.log10(data+1)
    #verse_time = verse_time.T
    #print(verse_time)
 
    fig = go.Figure()
    #fig.update_yaxes(title_text="Electron Energy", secondary_y=False)
    # Create the heatmap
    fig.add_trace(go.Heatmap(
        x=utctimes,
        y=f.HEPD_pro_energy_table.values.flatten(),
        z=data,
        colorscale=colormap,
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        #zmin=0,#np.min(data) if not log else None,
        #zmax=0.8,#np.max(data) if not log else None,
        #zsmooth='best'
    ))
    fig.update_layout(
        title="Protons Energy over UTC Time",
        xaxis_title="UTC Time",
        yaxis_title=f"{f.HEPD_pro_energy_table.Units}",
        yaxis=dict(type='log', title='Electron Energy (MeV)')
    )
    st.plotly_chart(fig)
#f = xr.open_dataset(path, phony_dims='sort')
 

def plot_electrons_counts_on_map(path):
    f = xr.open_zarr(path)
    data = f.HEPD_ele_counts
    LonLat = f.LonLat
    if LonLat.ndim == 3:
        longitude = LonLat[0, 0, :]
        latitude = LonLat[0, 0, :]
    elif LonLat.ndim == 2:
        longitude = LonLat[:, 0]
        latitude = LonLat[:, 1]
    else:
        raise ValueError("Unexpected LonLat dimensions")
    try:
        freq = data.shape[1]
    except IndexError:
        freq = 1
 
    measure = data.values.flatten()
 
    lon = longitude.values.flatten()
    lat = latitude.values.flatten()
 
    length_coord = len(lon)
    length_measure = len(measure)
 
    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
 
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])
 
    # Create a scatter plot on a map using Plotly
    fig = go.Figure()
 
    # Load world map using geopandas
    world = gpd.read_file('webappfiles/maps/ne_110m_admin_0_countries.shp')
 
    # Plot world map as background
    fig.add_trace(go.Choropleth(
        geojson=world.__geo_interface__,
        locations=world.index,
        z=np.zeros(len(world)),  # Dummy values for Choropleth trace
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        hoverinfo='none',
        showscale=False
    ))
 
    # Scatter plot for data points
    fig.add_trace(go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        mode='markers',
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="Counts"),
            opacity=0.8,
            colorbar_thickness=20,
            colorbar_x=0.85,
            colorbar_y=0.5,
            colorbar_bgcolor='rgba(255,255,255,0.5)'
        ),
        name="Field magnitude"
    ))
 
    fig.update_geos(
        projection_type="natural earth",
        landcolor="lightgrey",
        oceancolor="lightblue",
        showland=True,
        showocean=True,
        showcountries=True,
        showcoastlines=True,
        showframe=False,
        coastlinewidth=0.5,
        coastlinecolor="white"
    )
 
    fig.update_layout(
        title="Electrons counts during the orbit",
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth'
        ),
        geo_scope='world',
        height=600,
        margin={"r":0,"t":30,"l":0,"b":0},
        showlegend=False
    )
    st.plotly_chart(fig)
 
#f = xr.open_dataset(path, phony_dims='sort')
#LonLat= f.LonLat
#f = xr.open_zarr(path)
#f
 

def plot_protons_counts_on_map(path):
    f = xr.open_zarr(path)
    data = f.HEPD_pro_counts
    LonLat = f.LonLat
    if LonLat.ndim == 3:
        longitude = LonLat[0, 0, :]
        latitude = LonLat[0, 0, :]
    elif LonLat.ndim == 2:
        longitude = LonLat[:, 0]
        latitude = LonLat[:, 1]
    else:
        raise ValueError("Unexpected LonLat dimensions")
    try:
        freq = data.shape[1]
    except IndexError:
        freq = 1
 
    measure = data.values.flatten()
 
    lon = longitude.values.flatten()
    lat = latitude.values.flatten()
 
    length_coord = len(lon)
    length_measure = len(measure)
 
    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
 
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])
 
    # Create a scatter plot on a map using Plotly
    fig = go.Figure()

    # Load world map using geopandas
    world = gpd.read_file('webappfiles/maps/ne_110m_admin_0_countries.shp')
 
    # Plot world map as background
    fig.add_trace(go.Choropleth(
        geojson=world.__geo_interface__,
        locations=world.index,
        z=np.zeros(len(world)),  # Dummy values for Choropleth trace
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        hoverinfo='none',
        showscale=False
    ))
 
    # Scatter plot for data points
    fig.add_trace(go.Scattergeo(
        lon=lon_extend,
        lat=lat_extend,
        mode='markers',
        marker=dict(
            size=10,
            color=measure,
            colorscale='Viridis',
            colorbar=dict(title="Counts"),
            opacity=0.8,
            colorbar_thickness=20,
            colorbar_x=0.85,
            colorbar_y=0.5,
            colorbar_bgcolor='rgba(255,255,255,0.5)'
        ),
        name="Field magnitude"
    ))
 
    fig.update_geos(
        projection_type="natural earth",
        landcolor="lightgrey",
        oceancolor="lightblue",
        showland=True,
        showocean=True,
        showcountries=True,
        showcoastlines=True,
        showframe=False,
        coastlinewidth=0.5,
        coastlinecolor="white"
    )
 
    fig.update_layout(
        title="Proton counts during the orbit",
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth'
        ),
        geo_scope='world',
        height=600,
        margin={"r":0,"t":30,"l":0,"b":0},
        showlegend=False
    )
    st.plotly_chart(fig)
 
#f = xr.open_dataset(path, phony_dims='sort')
#LonLat= f.LonLat
#f = xr.open_zarr(path)
#f

def aggregate_HEPPD_electron_proton(files, count_type='electron'):
    fig = go.Figure()
 
    for file in files:
        f = xr.open_zarr(file)
 
        # Extract the required variables
        LonLat = f.LonLat
        if LonLat.ndim == 3:
            latitude = LonLat[0, 0, :]
        elif LonLat.ndim == 2:
            latitude = LonLat[:, 1]
 
        if count_type == 'electron':
            try:
                count_data = f['HEPD_ele_counts'][...]
            except:
                count_data = f['Count_Electron'][...]
        else:
            try:
                count_data = f['HEPD_pro_counts'][...]
            except:
                count_data = f['Count_Proton'][...]
 
        # Flatten the data for plotting
        latitude = latitude.values.flatten()
        count_data = count_data.values.flatten()
 
        # Plot the data
        fig.add_trace(
            go.Scatter(x=latitude, y=count_data, mode='lines', name=file)
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

def plot_HEPD(file_path):
    plot_proton_electron_count_utc(file_path)
    plot_electron_energy_utc(file_path)
    plot_proton_energy_utc(file_path)
    plot_electrons_counts_on_map(file_path)
    plot_protons_counts_on_map(file_path)