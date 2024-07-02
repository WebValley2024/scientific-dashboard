import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xarray as xr
import streamlit as st

def load_data(path):
    try:
        return xr.open_zarr(path)
    except:
        return xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')

def plot_proton_electron_count_verse_time(paths):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'cyan', 'magenta']

    for i, path in enumerate(paths):
        f = load_data(path)
        verse_time = f.VERSE_TIME
        try:
            data = f.Count_electron
            data2 = f.Count_proton
        except:
            data = f.Count_Electron
            data2 = f.Count_Proton

        data = data.values[50:].flatten()
        data2 = data2.values[50:].flatten()
        verse_time = verse_time.values[50:].flatten()
        len_time = len(verse_time)

        freq = data.shape[0] // len_time
        vers_extend = np.concatenate([np.linspace(verse_time[j], verse_time[j+1], freq, endpoint=False) for j in range(len_time-1)])
        vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])

        fig.add_trace(go.Scatter(x=vers_extend, y=data, name=f"Electron Count {i+1}", line=dict(color=colors[i % len(colors)])), secondary_y=False)
        fig.add_trace(go.Scatter(x=vers_extend, y=data2, name=f"Proton Count {i+1}", line=dict(dash='dot', color=colors[i % len(colors)])), secondary_y=True)

    fig.update_yaxes(title_text="Electron Count", secondary_y=False)
    fig.update_yaxes(title_text="Proton Count", secondary_y=True)
    fig.update_xaxes(title_text="Verse Time (ms)")
    fig.update_layout(title="Electron and Proton Counts over Time", template="plotly_white", autosize=False, width=800, height=600)
    st.plotly_chart(fig)

def plot_proton_electron_count_utc(paths):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'cyan', 'magenta']

    for i, path in enumerate(paths):
        f = load_data(path)
        time = f.UTC_TIME
        try:
            data = f.Count_electron
            data2 = f.Count_proton
        except:
            data = f.Count_Electron
            data2 = f.Count_Proton

        def convert_to_utc_time(date_strings):
            return pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)

        freq = data.shape[1] if len(data.shape) > 1 else 1
        data = data.values[1:].flatten()
        data2 = data2.values[1:].flatten()
        time = time.values[1:].flatten()

        len_time = len(time)
        time_extend = np.concatenate([np.linspace(time[j], time[j+1], freq, endpoint=False) for j in range(len_time-1)])
        time_extend = np.concatenate([time_extend, np.linspace(time[-2], time[-1], freq)])
        utctimes = convert_to_utc_time(time_extend)

        df = pd.DataFrame({"data": data, "data2": data2, "time": utctimes})
        fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name=f'Electron Count {i+1}', line=dict(color=colors[i % len(colors)])), secondary_y=False)
        fig.add_trace(go.Scatter(x=df['time'], y=df['data2'], mode='lines', name=f'Proton Count {i+1}', line=dict(dash='dot', color=colors[i % len(colors)])), secondary_y=True)

    fig.update_yaxes(title_text="Electron Counts", secondary_y=False)
    fig.update_yaxes(title_text="Proton Counts", secondary_y=True)
    fig.update_xaxes(title_text="Time (UTC)")
    fig.update_layout(title="Electron and Proton Counts", template="plotly_white", autosize=False, width=800, height=600)
    st.plotly_chart(fig)

def plot_on_map_electron_count(paths):
    fig = go.Figure()
    colors = ['Viridis', 'Cividis', 'Inferno', 'Magma', 'Plasma', 'Warm', 'Cool', 'Turbo', 'Ice', 'Edge']

    for i, path in enumerate(paths):
        f = load_data(path)
        latitude = f.GEO_LAT
        longitude = f.GEO_LON
        try:
            data = f.Count_electron
        except:
            data = f.Count_Electron

        measure = data.values[1:].flatten()
        lon = longitude.values[1:].flatten()
        lat = latitude.values[1:].flatten()
        length_coord = len(lon)
        freq = data.shape[1] if len(data.shape) > 1 else 1

        lon_extend = np.concatenate([np.linspace(lon[j], lon[j+1], freq, endpoint=False) for j in range(length_coord-1)])
        lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
        lat_extend = np.concatenate([np.linspace(lat[j], lat[j+1], freq, endpoint=False) for j in range(length_coord-1)])
        lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

        scatter = go.Scattergeo(lon=lon_extend, lat=lat_extend, text=measure, marker=dict(size=10, color=measure, colorscale=colors[i % len(colors)], colorbar=dict(title="Counts"), cmin=measure.min(), cmax=100, showscale=True), mode='markers')
        fig.add_trace(scatter)

    fig.update_layout(geo=dict(showland=True, landcolor="lightgrey"), autosize=False, width=800, height=600, title="Electron Counts", template="plotly_white")
    st.plotly_chart(fig)

def plot_on_map_proton_count(paths):
    fig = go.Figure()
    colors = ['Viridis', 'Cividis', 'Inferno', 'Magma', 'Plasma', 'Warm', 'Cool', 'Turbo', 'Ice', 'Edge']

    for i, path in enumerate(paths):
        f = load_data(path)
        latitude = f.GEO_LAT
        longitude = f.GEO_LON
        try:
            data = f.Count_proton
        except:
            data = f.Count_Proton

        measure = data.values[1:].flatten()
        lon = longitude.values[1:].flatten()
        lat = latitude.values[1:].flatten()
        length_coord = len(lon)
        freq = data.shape[1] if len(data.shape) > 1 else 1

        lon_extend = np.concatenate([np.linspace(lon[j], lon[j+1], freq, endpoint=False) for j in range(length_coord-1)])
        lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
        lat_extend = np.concatenate([np.linspace(lat[j], lat[j+1], freq, endpoint=False) for j in range(length_coord-1)])
        lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

        scatter = go.Scattergeo(lon=lon_extend, lat=lat_extend, text=measure, marker=dict(size=10, color=measure, colorscale=colors[i % len(colors)], colorbar=dict(title="Counts"), cmin=measure.min(), cmax=30, showscale=True), mode='markers')
        fig.add_trace(scatter)

    fig.update_layout(geo=dict(showland=True, landcolor="lightgrey"), autosize=False, width=800, height=600, title="Proton Counts", template="plotly_white")
    st.plotly_chart(fig)

def plot_electron_energy_verse(paths):
    fig = go.Figure()
    colormap = 'viridis'

    for i, path in enumerate(paths):
        f = load_data(path)
        verse_time = f.VERSE_TIME
        data = f.A411
        data = np.sum(data, axis=2)
        threshold = 1e-10
        freq = data.shape[1] if len(data.shape) > 1 else 1
        data = data.values[1:]
        verse_time = verse_time.values[1:].flatten()
        data[data < threshold] = np.nan
        data = data.T

        fig.add_trace(go.Heatmap(x=verse_time, y=f.Energy_Table_Electron.values.flatten(), z=data, colorscale=colormap, colorbar=dict(title='Particles/cm^2/s/str')))

    fig.update_layout(title='Electron Energy Spectrum', xaxis_title="Verse Time (ms)", yaxis_title="Energy (KeV)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig)

def plot_electron_energy_utc(paths):
    fig = go.Figure()
    colormap = 'viridis'

    for i, path in enumerate(paths):
        f = load_data(path)
        time = f.UTC_TIME
        data = f.A411
        data = np.sum(data, axis=2)
        threshold = 1e-10
        freq = data.shape[1] if len(data.shape) > 1 else 1
        data = data.values[1:]
        time = time.values[1:].flatten()
        data[data < threshold] = np.nan
        data = data.T

        fig.add_trace(go.Heatmap(x=time, y=f.Energy_Table_Electron.values.flatten(), z=data, colorscale=colormap, colorbar=dict(title='Particles/cm^2/s/str')))

    fig.update_layout(title='Electron Energy Spectrum', xaxis_title="Time (UTC)", yaxis_title="Energy (KeV)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig)

def plot_proton_energy_verse(paths):
    fig = go.Figure()
    colormap = 'viridis'

    for i, path in enumerate(paths):
        f = load_data(path)
        verse_time = f.VERSE_TIME
        data = f.A421
        data = np.sum(data, axis=2)
        threshold = 1e-10
        freq = data.shape[1] if len(data.shape) > 1 else 1
        data = data.values[1:]
        verse_time = verse_time.values[1:].flatten()
        data[data < threshold] = np.nan
        data = data.T

        fig.add_trace(go.Heatmap(x=verse_time, y=f.Energy_Table_Proton.values.flatten(), z=data, colorscale=colormap, colorbar=dict(title='Particles/cm^2/s/str')))

    fig.update_layout(title='Proton Energy Spectrum', xaxis_title="Verse Time (ms)", yaxis_title="Energy (KeV)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig)

def plot_proton_energy_utc(paths):
    fig = go.Figure()
    colormap = 'viridis'

    for i, path in enumerate(paths):
        f = load_data(path)
        time = f.UTC_TIME
        data = f.A421
        data = np.sum(data, axis=2)
        threshold = 1e-10
        freq = data.shape[1] if len(data.shape) > 1 else 1
        data = data.values[1:]
        time = time.values[1:].flatten()
        data[data < threshold] = np.nan
        data = data.T

        fig.add_trace(go.Heatmap(x=time, y=f.Energy_Table_Proton.values.flatten(), z=data, colorscale=colormap, colorbar=dict(title='Particles/cm^2/s/str')))

    fig.update_layout(title='Proton Energy Spectrum', xaxis_title="Time (UTC)", yaxis_title="Energy (KeV)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig)

def main():
    st.title("Scientific Data Analysis")

    uploaded_files = st.file_uploader("Upload Data Files", type=['zarr', 'h5'], accept_multiple_files=True)
    manual_paths = st.text_area("Or Enter File Paths (one per line)")
    predefined_paths = [
        "/home/wvuser/DATA SET tutorial/HEPPL/CSES_01_HEP_2_L02_A4_268450_20221204_081940_20221204_085644_000.zarr",
        "/home/wvuser/DATA SET tutorial/HEPPL/CSES_01_HEP_2_L02_A4_268441_20221204_073212_20221204_080924_000.zarr",
        "/home/wvuser/DATA SET tutorial/HEPPL/CSES_01_HEP_2_L02_A4_268450_20221204_082340_20221204_083324_000.zarr"
    ]
    paths = predefined_paths.copy()

    if uploaded_files:
        paths.extend([f.name for f in uploaded_files])
    
    if manual_paths:
        paths.extend(manual_paths.splitlines())

    if not paths:
        st.info("Please upload at least one data file or enter file paths.")
        return

    # Plotting options
    plot_type = st.selectbox("Select Plot Type", ["Proton and Electron Count vs Time", "Proton and Electron Count UTC", "Electron Count on Map", "Proton Count on Map", "Electron Energy vs Time", "Electron Energy UTC", "Proton Energy vs Time", "Proton Energy UTC"])

    # Plot based on selection
    if plot_type == "Proton and Electron Count vs Time":
        plot_proton_electron_count_verse_time(paths)
    elif plot_type == "Proton and Electron Count UTC":
        plot_proton_electron_count_utc(paths)
    elif plot_type == "Electron Count on Map":
        plot_on_map_electron_count(paths)
    elif plot_type == "Proton Count on Map":
        plot_on_map_proton_count(paths)
    elif plot_type == "Electron Energy vs Time":
        plot_electron_energy_verse(paths)
    elif plot_type == "Electron Energy UTC":
        plot_electron_energy_utc(paths)
    elif plot_type == "Proton Energy vs Time":
        plot_proton_energy_verse(paths)
    elif plot_type == "Proton Energy UTC":
        plot_proton_energy_utc(paths)

if __name__ == "__main__":
    main()
