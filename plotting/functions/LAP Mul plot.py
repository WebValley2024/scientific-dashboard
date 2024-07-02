import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import pandas as pd
import numpy as np

# Function to reduce frequency of data
def reduce_frequency(data, factor):
    # Your implementation here
    return data

def lap_plot(f_paths):
    # Create a subplots with two rows and one column, specifying secondary_y=True for each subplot
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
    
    # Function to plot Electron Temperature and Electron Density over UTC time
    def plot_twin_timeline_utc(fig, paths):
        for path in paths:
            f = xr.open_zarr(path)
            
            # Extract the required variables
            time = f['UTC_TIME'][...].values.flatten()
            data = f['A311'][...]
            data2 = f['A321'][...]
            
            # Reduce the frequency of the data
            data = reduce_frequency(data, 1)
            data2 = reduce_frequency(data2, 1)
            
            log = True
        
            def convert_to_utc_time(date_strings):
                utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
                return utc_times
        
            # Catch all problems with frequency
            try:
                freq = data.shape[1]
            except:
                freq = 1
            
            # Remove the first element of the data and flatten it to be able to plot it
            data = data.values[1:].flatten()
            data2 = data2.values[1:].flatten()
            
            # Remove the first element of the time and flatten it
            time = time[1:]
            
            len_time = len(time)
            time_extend = np.concatenate([np.linspace(time[i], time[i+1], freq, endpoint=False) for i in range(len_time - 1)])
            time_extend = np.concatenate([time_extend, np.linspace(time[-2], time[-1], freq)])
            utctimes = convert_to_utc_time(time_extend)
            
            df = pd.DataFrame({
                "data": data,
                "data2": data2,
                "time": utctimes
            })
        
            # Plotting with Plotly
            fig.add_trace(go.Scatter(x=df['time'], y=df['data'], mode='lines', name='Electron Density'), row=1, col=1, secondary_y=False)
            fig.add_trace(go.Scatter(x=df['time'], y=df['data2'], mode='lines', name='Electron Temperature', line=dict(color='red')), row=1, col=1, secondary_y=True)
        
        # Update y-axes titles
        fig.update_yaxes(title_text="1/m^3", secondary_y=False, row=1, col=1)
        fig.update_yaxes(title_text="K", secondary_y=True, row=1, col=1)
        if log:
            fig.update_yaxes(type="log", secondary_y=False, row=1, col=1)
            fig.update_yaxes(type="log", secondary_y=True, row=1, col=1)
        
        # Update x-axis title
        fig.update_xaxes(title_text="Time (UTC)", row=1, col=1)
        
        return fig
    
    # Function to plot Electron Density and Electron Temperature over Verse Time
    def plot_twin_timeline_verse_time(fig, paths):
        for path in paths:
            f = xr.open_zarr(path)
            
            # Extract the required variables
            verse_time = f['VERSE_TIME'][...].values.flatten()
            data = f['A311'][...]
            data2 = f['A321'][...]
            
            # Reduce the frequency of the data
            data = reduce_frequency(data, 1)
            data2 = reduce_frequency(data2, 1)
            
            log = True
            
            # Get the frequency dimension
            try:
                freq = data.shape[1]
            except:
                freq = 1
            
            # Remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
            data = data.values[1:].flatten()
            data2 = data2.values[1:].flatten()
            
            # Remove the first element of the verse time and flatten it
            verse_time = verse_time[1:]
            
            # Get the length to be able to plot it
            len_time = len(verse_time)
            
            # Plot everything
            vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
            vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
            
            # Add traces to the figure
            fig.add_trace(go.Scatter(x=vers_extend, y=data, name="Electron Density", line=dict(color='blue')), row=2, col=1, secondary_y=False)
            
            fig.add_trace(go.Scatter(x=vers_extend, y=data2, name="Electron Temperature", line=dict(color='red')), row=2, col=1, secondary_y=True)
        
        # Configure y-axes
        fig.update_yaxes(title_text="1/m^3", secondary_y=False, row=2, col=1)
        fig.update_yaxes(title_text="K", secondary_y=True, row=2, col=1)
        if log:
            fig.update_yaxes(type="log", secondary_y=False, row=2, col=1)
            fig.update_yaxes(type="log", secondary_y=True, row=2, col=1)
        
        # Configure x-axis
        fig.update_xaxes(title_text="ms", row=2, col=1)
        
        return fig
    
    # Plotting on the first row
    plot_twin_timeline_utc(fig, f_paths)
    
    # Plotting on the second row
    plot_twin_timeline_verse_time(fig, f_paths)
    
    # Adjust layout and display the plot
    fig.update_layout(height=800, width=1200, title_text="Electron Density and Temperature")
    st.plotly_chart(fig)

# Example usage:
file_paths = [
    '/home/wvuser/DATA SET tutorial/HEPPL/CSES_01_LAP_1_L02_A3_027340_20180801_015614_20180801_023341_000.zarr',
    '/home/wvuser/DATA SET tutorial/HEPPL/CSES_01_LAP_1_L02_A3_027331_20180801_010858_20180801_014612_000.zarr',
    # Add more paths as needed
]

lap_plot(file_paths)
