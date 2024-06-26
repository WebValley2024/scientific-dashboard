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
    verse_time = verse_time.values[1:]
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
