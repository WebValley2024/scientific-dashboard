import numpy as np
import pandas as pd
import xarray as xr
import plotly.graph_objs as go

def convert_to_utc_time(date_strings):
    utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
    return utc_times

def plot_spectrogram(z_data, x_data, y_data, title, x_title, y_title):
    fig = go.Figure(go.Heatmap(
        z=z_data.T,  # Transpose the data for correct orientation
        x=x_data,
        y=y_data,
        colorscale='Viridis',
        colorbar=dict(title='Particles/cm²/s/sr/MeV')
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=dict(x=1, y=0.5)
    )

    fig.show()

def plot_variables(file_path):
    with xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort') as f:
        data = {
            'UTC_TIME': f['UTC_TIME'][:].values.flatten(),
            'A411': f['A411'][:].values,
            'A412': f['A412'][:].values,
            'Energy_Table_Electron': f['Energy_Table_Electron'][:].values,
            'Energy_Table_Proton': f['Energy_Table_Proton'][:].values
        }
    
    # Convert and extend time data
    time = data['UTC_TIME']
    freq = data['A411'].shape[1] if len(data['A411'].shape) > 1 else 1
    time = time[1:]
    len_time = len(time)
    time_extend = np.concatenate([np.linspace(time[i], time[i+1], freq, endpoint=False) for i in range(len_time - 1)])
    time_extend = np.concatenate([time_extend, np.linspace(time[-2], time[-1], freq)])
    utctimes = convert_to_utc_time(time_extend)
    
    # Electron Energy Spectrum
    a411_data = np.reshape(data['A411'], (-1, 256, 9))
    a411_data_mean = np.mean(a411_data, axis=0)
    plot_spectrogram(a411_data_mean, utctimes, np.arange(256), 
                     "Electron Energy Spectrum", "Time (UTC)", "Energy (MeV)")

    # Electron Pitch Angle Spectrum
    a411_pitch_angle_mean = np.mean(a411_data, axis=1)
    plot_spectrogram(a411_pitch_angle_mean, utctimes, np.arange(9), 
                     "Electron Pitch Angle Spectrum", "Time (UTC)", "Pitch Angle (degrees)")

    # Proton Energy Spectrum
    a412_data = np.reshape(data['A412'], (-1, 256, 9))
    a412_data_mean = np.mean(a412_data, axis=0)
    plot_spectrogram(a412_data_mean, utctimes, np.arange(256), 
                     "Proton Energy Spectrum", "Time (UTC)", "Energy (MeV)")

    # Proton Pitch Angle Spectrum
    a412_pitch_angle_mean = np.mean(a412_data, axis=1)
    plot_spectrogram(a412_pitch_angle_mean, utctimes, np.arange(9), 
                     "Proton Pitch Angle Spectrum", "Time (UTC)", "Pitch Angle (degrees)")

# Example usage with the provided file path
file_path = '/home/wvuser/DATA SET tutorial/webvalley2024_EP_tutorial/webvalley2024/WebValley 2024 Challenge 2/CSES_01_HEP_1_L02_A4_176401_20210407_182209_20210407_190029_000 (1).h5'
plot_variables(file_path)
