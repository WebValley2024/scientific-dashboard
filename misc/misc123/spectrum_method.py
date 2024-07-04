import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import xarray as xr
from datetime import datetime, timezone

'''      
how to use:
-first define the path and extract the file using xarray:

path = "YOUR PATH"
f = xr.open_dataset(path, phony_dims='sort')


-select the file that has the data in it:
-example:
data = f['A141_W'][...]

IMPORTANT: Only use with 2d arrays: 
print(data.shape)
if it looks like this:
(int, int)
it is a 2d array

define verse_time:

verse_time = f['VERSE_TIME'] (may be different in some payloads)

call the function
plot_spectrum(data, verse_time)
'''
def plot_spectrum(data, verse_time, log=True, colormap='viridis'):
    # Catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1

    # Catch all problems with units
    unit = ""
    try:
        unit = data.attrs.get('Unit', '')  # Try accessing 'Unit' attribute
    except AttributeError:
        try:
            unit = data.attrs.get('units', '')  # If 'Unit' attribute is not found, try 'unit' attribute
        except AttributeError:
            pass  # If neither attribute is found, do nothing
    
    verse_time_unit = ""
    try:
        verse_time_unit = verse_time.attrs.get('Unit', '')  # Try accessing 'Unit' attribute
    except AttributeError:
        try:
            verse_time_unit = verse_time.attrs.get('units', '')  # If 'Unit' attribute is not found, try 'unit' attribute
        except AttributeError:
            pass  # If neither attribute is found, do nothing

    # Catch all problems with titles
    name = ""
    try:
        name = data.attrs.get('long_name', '')
    except:
        pass

    # Remove the first element of the data (it sometimes gives weird values)
    data = data.values[1:]
    verse_time = verse_time.values[1:]

    # Get the length to be able to plot it
    len_time = len(verse_time)

    # Define the parameters
    plt.figure(figsize=(10, 6))
    plt.title(name)
    
    # Create a 2D plot with the first dimension as the x-axis (verse time) and the second dimension as the y-axis (hue)
    time_grid, freq_grid = np.meshgrid(verse_time, np.arange(data.shape[1]))

    # Transpose data for correct orientation
    data = data.T
    
    # Plot the spectrum using pcolormesh
    norm = colors.LogNorm() if log else None
    plt.pcolormesh(time_grid, freq_grid, data, shading='auto', norm=norm, cmap=colormap)
    
    # Colorbar for the spectrum
    cbar = plt.colorbar()
    cbar.set_label(unit)

    # Label the axes
    plt.ylabel('Frequency Index')
    plt.xlabel(verse_time_unit)

    # show the plot
    plt.show()
