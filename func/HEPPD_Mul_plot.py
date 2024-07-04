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
    fig5 = go.Figure()

    for path in file_paths:
        try:
            f = xr.open_zarr(path)
        except:
            f = xr.open_dataset(path, engine='netcdf4')

        # Extract data
        time = f.UTCTime.values[1:].flatten()
        data1 = f.HEPD_ele_counts.values[1:].flatten()
        data2 = f.HEPD_pro_counts.values[1:].flatten()
        energies_electron = np.sum(f.HEPD_ele_energy_pitch.values[1:], axis=2)
        energies_proton = np.sum(f.HEPD_pro_energy_pitch.values[1:], axis=2)
        LonLat = f.LonLat

        # Prepare data for plotting
        utctimes = pd.to_datetime(time, format="%Y%m%d%H%M%S%f", utc=True)
        
        if LonLat.ndim == 3:
            longitude = LonLat[0, 0, :].values.flatten()
            latitude = LonLat[0, 1, :].values.flatten()
        elif LonLat.ndim == 2:
            longitude = LonLat[:, 0].values.flatten()
            latitude = LonLat[:, 1].values.flatten()
        else:
            raise ValueError("Unexpected LonLat dimensions")

        lon_extend = np.concatenate([np.linspace(longitude[i], longitude[i + 1], len(data1), endpoint=False) for i in range(len(longitude) - 1)])
        lon_extend = np.concatenate([lon_extend, np.linspace(longitude[-2], longitude[-1], len(data1))])
        lon_extend = reduce_frequency(lon_extend, 1)  # Downsampling

        lat_extend = np.concatenate([np.linspace(latitude[i], latitude[i + 1], len(data1), endpoint=False) for i in range(len(latitude) - 1)])
        lat_extend = np.concatenate([lat_extend, np.linspace(latitude[-2], latitude[-1], len(data1))])
        lat_extend = reduce_frequency(lat_extend, 1)  # Downsampling

        data1_downsampled = reduce_frequency(data1, 1)
        data2_downsampled = reduce_frequency(data2, 2)

        # Plotting data
        fig1.add_trace(go.Scatter(x=utctimes, y=data1, mode='lines', name = f'{orbit_number(path)}- Electron Count'))
        fig1.add_trace(go.Scatter(x=utctimes, y=data2 + 100, mode='lines', name = f'{orbit_number(path)}- Proton Count', line=dict(color='red')))

        fig2.add_trace(go.Heatmap(
            x=utctimes,
            y=f.HEPD_ele_energy_table.values.flatten(),
            z=np.log10(energies_electron.T + 1),
            colorscale='viridis',
            colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
            name=f'{orbit_number(path)}- Electron Energy'
        ))

        fig3.add_trace(go.Heatmap(
            x=utctimes,
            y=f.HEPD_pro_energy_table.values.flatten(),
            z=np.log10(energies_proton.T + 1),
            colorscale='viridis',
            colorbar=dict(title='Log10(Particles/cm^2/s/str)'),
            name=f'{orbit_number(path)} - Proton Energy'
        ))

        fig4.add_trace(go.Scattergeo(
            lon=lon_extend,
            lat=lat_extend,
            mode='markers',
            marker=dict(
                size=10,
                color=data1_downsampled,
                colorscale='Viridis',
                colorbar=dict(title="Counts"),
                opacity=0.8,
                colorbar_thickness=20,
                colorbar_x=0.85,
                colorbar_y=0.5,
                colorbar_bgcolor='rgba(255,255,255,0.5)'
            ),
            name=f'{orbit_number(path)}- Electron Counts'
        ))

        fig5.add_trace(go.Scattergeo(
            lon=lon_extend,
            lat=lat_extend,
            mode='markers',
            marker=dict(
                size=10,
                color=data2_downsampled,
                colorscale='Viridis',
                colorbar=dict(title="Counts"),
                opacity=0.8,
                colorbar_thickness=20,
                colorbar_x=0.85,
                colorbar_y=0.5,
                colorbar_bgcolor='rgba(255,255,255,0.5)'
            ),
            name=f'{orbit_number(path)} - Proton Counts'
        ))

    # Update layout for fig1
    fig1.update_yaxes(title_text="Electron Counts", secondary_y=False)
    fig1.update_yaxes(title_text="Proton Counts", secondary_y=True)
    fig1.update_xaxes(title_text="Time (UTC)")
    fig1.update_layout(
        title="Electron and Proton Counts",
        template="plotly_white",
        autosize=True,
        width=800,
        height=600
    )

    # Update layout for fig2
    fig2.update_layout(
        title="Electron Energy over UTC Time",
        xaxis_title="UTC Time",
        yaxis_title="Electron Energy (MeV)",
    )

    # Update layout for fig3
    fig3.update_layout(
        title="Proton Energy over UTC Time",
        xaxis_title="UTC Time",
        yaxis_title="Proton Energy (MeV)",
    )

    # Load world map using geopandas
    world = gpd.read_file('webappfiles/maps/ne_110m_admin_0_countries.shp')

    # Plot world map as background for fig4 and fig5
    for fig in [fig4, fig5]:
        fig.add_trace(go.Choropleth(
            geojson=world.__geo_interface__,
            locations=world.index,
            z=np.zeros(len(world)),  # Dummy values for Choropleth trace
            colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
            hoverinfo='none',
            showscale=False
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

    # Streamlit plotting
    return fig1, fig2, fig3
    # st.plotly_chart(fig1)
    # st.plotly_chart(fig2)
    # st.plotly_chart(fig3)
    # st.plotly_chart(fig4)
    # st.plotly_chart(fig5)

def reduce_frequency(data_array, factor):
    if data_array.ndim == 1:
        return data_array[::factor]
    elif data_array.ndim == 2:
        num_rows, num_cols = data_array.shape
        return data_array[::factor, ::factor]
    else:
        raise ValueError("Unsupported array dimensions")

# Example usage:
# file_paths = ["path_to_file1.zarr", "path_to_file2.zarr"]
# plot_HEPD_multiple_files(file_paths)


def orbit_number(filename):
    # Split the filename by underscores
    parts = filename.split('_')
    
    # The desired number is in the 6th position (index 5)
    number = parts[6]
    
    return number
