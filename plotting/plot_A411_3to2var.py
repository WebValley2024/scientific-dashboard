import numpy as np
import xarray as xr
import plotly.graph_objs as go

def plot_a411_spectrum(file_path):
    try:
        with xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort') as f:
            # Load A411 data
            a411_data = f['A411'].values
            
            # Dimensions
            num_energy_channels = 256
            num_pitch_angles = 9
            
            # Reshape data for plotting (assuming dimensions are [N, 256, 9])
            a411_data = np.reshape(a411_data, (-1, num_energy_channels, num_pitch_angles))
            
            # Take mean across the first dimension (if necessary)
            a411_data = np.mean(a411_data, axis=0)  # Adjust if different aggregation is needed
            
            # Plotting
            fig = go.Figure(data=go.Heatmap(
                z=a411_data.T,  # Transpose for correct orientation
                colorscale='Viridis',
                colorbar=dict(title='Intensity'),
                x=np.arange(num_energy_channels),  # Energy channels
                y=np.arange(num_pitch_angles)  # Pitch angles
            ))

            fig.update_layout(
                title="Electron Energy & Pitch Angle Spectrum (A411)",
                xaxis_title="Energy Channels",
                yaxis_title="Pitch Angles",
                legend=dict(x=1, y=0.5)
            )

            fig.show()

    except FileNotFoundError:
        print(f"File not found at: {file_path}")

# Example usage with the provided file path
file_path = '/home/wvuser/DATA SET tutorial/webvalley2024_EP_tutorial/webvalley2024/WebValley 2024 Challenge 2/CSES_01_HEP_1_L02_A4_176401_20210407_182209_20210407_190029_000 (1).h5'
plot_a411_spectrum(file_path)
