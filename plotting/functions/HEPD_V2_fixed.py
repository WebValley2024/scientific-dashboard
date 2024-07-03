import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xarray as xr
import geopandas as gpd

def plot_proton_electron_count_utc(path):
    st.write("herhehre")
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

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    try:
        freq = data.shape[1]
    except:
        freq = 1

    data = data.values[1:].flatten()
    data2 = data2.values[1:].flatten()
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

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Electron Count'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['time'], y=df['data2'], mode='lines', name='Proton Count', line=dict(color='red')), secondary_y=True)

    fig.update_yaxes(title_text="Electron Counts", secondary_y=False)
    fig.update_yaxes(title_text="Proton Counts", secondary_y=True)

    fig.update_xaxes(title_text="Time (UTC)")

    fig.update_layout(
        title="Electron and Proton Counts",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600
    )

    st.plotly_chart(fig)

def plot_spectrogram(data, time, pitch_table, title, yaxis_title):
    data = np.sum(data, axis=2)
    data = data.values[1:]
    time = time.values[1:].flatten()
    utctimes = pd.to_datetime(time, format="%Y%m%d%H%M%S%f", utc=True)
    data[data == 0] = np.nan
    data = np.log10(data.T + 1)
    
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        x=utctimes,
        y=pitch_table.values.flatten(),
        z=data,
        colorscale='viridis',
        colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
    ))
    fig.update_layout(
        title=title,
        xaxis_title="UTC Time",
        yaxis_title=yaxis_title,
    )
    st.plotly_chart(fig)

def plot_electron_energy_utc(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    plot_spectrogram(f.HEPD_ele_energy_pitch, f.UTCTime, f.HEPD_ele_energy_table, 
                     "Electron Energy over UTC Time", f.HEPD_ele_energy_table.Units)

def plot_proton_energy_utc(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    plot_spectrogram(f.HEPD_pro_energy_pitch, f.UTCTime, f.HEPD_pro_energy_table, 
                     "Proton Energy over UTC Time", f.HEPD_pro_energy_table.Units)

def plot_electron_pitch_utc(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    plot_spectrogram(f.HEPD_ele_pitch_table, f.UTCTime, f.HEPD_ele_pitch_table, 
                     "Electron Pitch over UTC Time", "Pitch Angle (degrees)")

def plot_proton_pitch_utc(path):
    f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
    plot_spectrogram(f.HEPD_pro_pitch_table, f.UTCTime, f.HEPD_pro_pitch_table, 
                     "Proton Pitch over UTC Time", "Pitch Angle (degrees)")

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

    fig = go.Figure()
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    fig.add_trace(go.Choropleth(
        geojson=world.__geo_interface__,
        locations=world.index,
        z=np.zeros(len(world)),
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        hoverinfo='none',
        showscale=False
    ))

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

    fig = go.Figure()
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    fig.add_trace(go.Choropleth(
        geojson=world.__geo_interface__,
        locations=world.index,
        z=np.zeros(len(world)),
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        hoverinfo='none',
        showscale=False
    ))

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
        title="Protons counts during the orbit",
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

def plot_HEPPD(path):
    plot_proton_electron_count_utc(path)
    
    st.header("Electron Energy Spectrum")
    plot_electron_energy_utc(path)
    
    st.header("Proton Energy Spectrum")
    plot_proton_energy_utc(path)
    
    st.header("Electron Pitch Angle")
    plot_electron_pitch_utc(path)
    
    st.header("Proton Pitch Angle")
    plot_proton_pitch_utc(path)
    
    st.header("Electron Counts on Map")
    plot_electrons_counts_on_map(path)
    
    st.header("Proton Counts on Map")
    plot_protons_counts_on_map(path)
