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
 




def plot_against_verse_time(data, verse_time, log=True):
    try:
        freq = data.shape[1]
    except:
        freq = 1

    
    unit = ""
    try:
        unit = data.Unit  # Try accessing 'Unit' attribute
    except AttributeError:
        try:
            unit = data.units  # If 'Unit' attribute is not found, try 'unit' attribute
        except AttributeError:
            pass  # If neither attribute is found, do nothing
   
   
 
    name = ""
    try:
        name = data.long_name
    except:
        pass
 
    data=data.values[1:].flatten()
 
    verse_time = verse_time.values[1:]
    len_time = len(verse_time)
    vers_extend = np.concatenate([np.linspace(verse_time[i], verse_time[i+1], freq, endpoint=False) for i in range(len_time-1)])
    vers_extend = np.concatenate([vers_extend, np.linspace(verse_time[-2], verse_time[-1], freq)])
 
 
    plt.figure(figsize=(8,6))
    plt.title(name)
    plt.plot(vers_extend, data)
    if log==True:
        plt.yscale('log')   
    plt.ylabel(unit)
    plt.xlabel("ms")
    plt.show()