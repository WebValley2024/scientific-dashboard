import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xarray as xr
import geopandas as gpd

def plot_HEPD_multiple_files(file_paths):
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2 = go.Figure()
    fig3 = go.Figure()
    fig4 = go.Figure()

    for path in file_paths:
        # Open dataset
        try:
            f = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
            data_type = 'netcdf'
        except:
            f = xr.open_zarr(path)
            data_type = 'zarr'

        # Extract data based on data_type
        if data_type == 'netcdf':
            time = f.UTCTime.values[1:].flatten()
            data1 = f.HEPD_ele_counts.values[1:].flatten()
            data2 = f.HEPD_pro_counts.values[1:].flatten()
            energies_electron = np.sum(f.HEPD_ele_energy_pitch.values[1:], axis=2)
            energies_proton = np.sum(f.HEPD_pro_energy_pitch.values[1:], axis=2)
            LonLat = f.LonLat
        else:  # zarr
            time = f.UTCTime.values[1:].flatten()
            data1 = f.HEPD_ele_counts.values[1:].flatten()
            data2 = f.HEPD_pro_counts.values[1:].flatten()
            energies_electron = np.sum(f.HEPD_ele_energy_pitch.values[1:], axis=2)
            energies_proton = np.sum(f.HEPD_pro_energy_pitch.values[1:], axis=2)
            LonLat = f.LonLat

        # Prepare data for plotting
        utctimes = pd.to_datetime(time, format="%Y%m%d%H%M%S%f", utc=True)
        data = {
            'time': utctimes,
            'data1': data1,
            'data2': data2,
            'energies_electron': energies_electron,
            'energies_proton': energies_proton
        }

        lon_lat = None
        if LonLat.ndim == 3:
            longitude = LonLat[0, 0, :].values.flatten()
            latitude = LonLat[0, 0, :].values.flatten()
        elif LonLat.ndim == 2:
            longitude = LonLat[:, 0].values.flatten()
            latitude = LonLat[:, 1].values.flatten()
        else:
            raise ValueError("Unexpected LonLat dimensions")

        if data_type == 'netcdf':
            freq = f.HEPD_ele_counts.shape[1]
            measure = f.HEPD_ele_counts.values.flatten()
        else:
            freq = f.HEPD_pro_counts.shape[1]
            measure = f.HEPD_pro_counts.values.flatten()

        lon_extend = np.concatenate([np.linspace(lon[i], lon[i + 1], freq, endpoint=False) for i in range(len(longitude) - 1)])
        lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])

        lat_extend = np.concatenate([np.linspace(lat[i], lat[i + 1], freq, endpoint=False) for i in range(len(latitude) - 1)])
        lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

        df = {
            "lon": lon_extend,
            "lat": lat_extend,
            "counts": measure
        }

        # Plotting data
        fig1.add_trace(go.Scatter(x=data['time'], y=data['data1'], mode='lines', name='Electron Count'))
        fig1.add_trace(go.Scatter(x=data['time'], y=data['data2'] + 100, mode='lines', name='Proton Count', line=dict(color='red')))

        fig2.add_trace(go.Heatmap(
            x=data['time'],
            y=f.HEPD_ele_energy_table.values.flatten(),
            z=data['energies_electron'],
            colorscale='viridis',
            colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        ))

        fig3.add_trace(go.Heatmap(
            x=data['time'],
            y=f.HEPD_pro_energy_table.values.flatten(),
            z=data['energies_proton'],
            colorscale='viridis',
            colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
        ))

        fig4.add_trace(go.Scattergeo(
            lon=df['lon'],
            lat=df['lat'],
            mode='markers',
            marker=dict(
                size=10,
                color=df['counts'],
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

    fig1.update_yaxes(title_text="Electron Counts", secondary_y=False)
    fig1.update_yaxes(title_text="Proton Counts", secondary_y=True)
    fig1.update_xaxes(title_text="Time (UTC)")

    fig1.update_layout(
        title="Electron and Proton Counts",
        template="plotly_white",
        autosize=False,
        width=800,
        height=600
    )

    fig2.update_layout(
        title="Electron Energy over UTC Time",
        xaxis_title="UTC Time",
        yaxis_title="Electron Energy (MeV)",
    )

    fig3.update_layout(
        title="Proton Energy over UTC Time",
        xaxis_title="UTC Time",
        yaxis_title="Proton Energy (MeV)",
    )

    fig4.update_geos(
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

    fig4.update_layout(
        title="Electrons/Protons counts during the orbit",
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth'
        ),
        geo_scope='world',
        height=600,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        showlegend=False
    )

    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
    st.plotly_chart(fig4)

# Example usage:
file_paths = [
    'path_to_file_1.nc',
    'path_to_file_2.nc',
    # Add more paths as needed
]

plot_HEPD_multiple_files(file_paths)
