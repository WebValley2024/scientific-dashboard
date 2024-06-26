import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import geopandas as gpd
import pandas as pd
import xarray
from datetime import datetime, timezone

# enlarge the size of the plot xlabel/ylabel

plt.rcParams.update({'font.size': 20})

""" 
This method plots the orbit with scalar measurements coded as colors along the orbit.
data = something like f.HEPD_ele_counts
longitude and latitude are normally accessed by f.GEO_LON or f.GEO_LAT. hower sometimes
there only is f.LonLat in that case:
lonlat = f.LonLat
lat = lonlat[:, 1]
lon = lonlat[:,0]

optional parameter: decide if the scale is not logarithmic (log = False). if there are negative values,
don't use log = True.
This method removes the first sample (made in the first second) as this often contains errors
If there are units and a title provided by the data we include it in the plot, otherwise we don't.
 """
def plot_on_map(data, longitude, latitude, log=True):
   
   
    unit = ""
    try:
        unit = data.Unit  # Try accessing 'Unit' attribute
    except AttributeError:
        try:
            unit = data.units  # If 'Unit' attribute is not found, try 'unit' attribute
        except AttributeError:
            pass  # If neither attribute is found, do nothing
   
    try:
        freq = data.shape[1]
    except:
        freq = 1
 
    name = ""
    try:
        name = data.long_name
    except:
        pass
 
    measure=data.values

    measure = measure[1:]
 
    measure.flatten()
 
 
    lon = longitude.values[1:].flatten()
 
    lat = latitude.values[1:].flatten()
    
    length_coord = len(lon)
 
    length_measure = len(measure)
 
 
    lon_extend = np.concatenate([np.linspace(lon[i], lon[i+1], freq, endpoint=False) for i in range(length_coord-1)])
 
    lon_extend = np.concatenate([lon_extend, np.linspace(lon[-2], lon[-1], freq)])
 
 
    lat_extend = np.concatenate([np.linspace(lat[i], lat[i+1], freq, endpoint=False) for i in range(length_coord-1)])
 
    lat_extend = np.concatenate([lat_extend, np.linspace(lat[-2], lat[-1], freq)])

 
    plt.figure(figsize=(8, 6))
 
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')) # needs geopandas 0.9.0 or older
 
    world.plot(color='lightgrey')
    if log==True:
        scatter = plt.scatter(lon_extend, lat_extend, c=measure, cmap='viridis', s=10, norm=LogNorm())
    else:
        scatter = plt.scatter(lon_extend, lat_extend, c=measure, cmap='viridis', s=10)
 
    plt.colorbar(scatter, label=unit)
 
    plt.title(name, fontsize=10)
 
    plt.xlabel('Longitude (deg)', fontsize=10)
 
    plt.ylabel('Latitude (deg)', fontsize=10)
 
    #plt.legend()
 
    plt.show()
 

#k = "data/CSES_01_EFD_1_L02_A1_213330_20211206_164953_20211206_172707_000.h5"
#b = xr.open_dataset(k, phony_dims='sort')




'''
to use:
-must install all the librarys and import:
 
import h5py
import xarray as xr
 
- must extract the file from the path:
 
k = "YOUR PATH TO THE FILE"
b = xr.open_dataset(k, phony_dims='sort')
 
- must define the payload sensor that u want to use.
- example:
 
X_Waveform = b['A111_W'][...]
 
-must define verse time:
 
relative_time = b['VERSE_TIME'][...]
(May be different depending on the payload!)
 
-call the function like this:
 
plot_against_verse_time(b, relative_time)
 
-If u want the plot in linear form:
 
plot_against_verse_time(b, relative_time, False)
'''
def plot_against_verse_time(data, verse_time, log=True):
    #catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
 
    #catch all problems with units
    unit = ""
    try:
        unit = data.Unit  # Try accessing 'Unit' attribute
    except AttributeError:
        try:
            unit = data.units  # If 'Unit' attribute is not found, try 'unit' attribute
        except AttributeError:
            pass  # If neither attribute is found, do nothing
    verse_time_unit = ""
    try:
        verse_time_unit = verse_time.Unit  # Try accessing 'Unit' attribute
    except AttributeError:
        try:
            verse_time_unit = verse_time.units  # If 'Unit' attribute is not found, try 'unit' attribute
        except AttributeError:
            pass  # If neither attribute is found, do nothing
   
   #catch all problems with titles
    name = ""
    try:
        name = data.long_name
    except:
        pass
 
    #remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data=data.values[1:].flatten()
 
    #do the same with the verse time
    verse_time = verse_time.values[1:].flatten()
    #get the length to be able to plot it
    len_time = len(verse_time)
 
    #plot everything
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
 
    #define the parameters
    plt.figure(figsize=(8,6))
    plt.title(name)
    plt.plot(vers_extend, data)
    #select if the scale is linear or logarithmic
    if log==True:
        plt.yscale('log')  
    plt.ylabel(unit) #plot data units
    plt.xlabel(verse_time_unit) #may not be ms
    plt.show()





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


"""
this is still in progress: used as the other methods above. however here we only plot data till the index
ix you can set in the code. if this index is too large, the machine crashes and it takes forever to calculate.
TODO: decide how we want to deal with this. plotting only 1 point per second? 2? We could also hand this over 
as a parameter I guess.
"""
def plot_against_utc(data, time):

    def convert_to_utc_time(date_strings):
        utc_times = pd.to_datetime(date_strings, format="%Y%m%d%H%M%S%f", utc=True)
        return utc_times

    # catch all problems with frequency
    try:
        freq = data.shape[1]
    except:
        freq = 1
    # catch all problems with units
    unit = ""
    try:
        unit = data.Unit  # Try accessing 'Unit' attribute
    except AttributeError:
        try:
            unit = data.units  # If 'Unit' attribute is not found, try 'unit' attribute
        except AttributeError:
            pass  # If neither attribute is found, do nothing
    verse_time_unit = ""
    # catch all problems with titles
    name = ""
    try:
        name = data.long_name
    except:
        pass
    # remove the first element of the data (it sometimes gives weird values) and flatten it to be able to plot it
    data = data.values[1:].flatten()
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

    ix = 3000 #3000000

    dd = pd.DataFrame({
        "data": data[:ix],
        "time": utctimes[:ix]
    })

    dd.plot(x="time", y="data")






    
