# %%
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pandas as pd
import xarray as xr
from datetime import datetime, timezone
from glob import glob
import pandas
import osmnx
import geopandas
import geodatasets
import rioxarray
import xarray
import datashader as ds
import contextily as cx
from shapely import geometry

# %%
EFD1 = 'CSES_data/CSES_01_EFD_1_L02_A1_213330_20211206_164953_20211206_172707_000.h5'
HEP1 = 'CSES_data/CSES_01_HEP_1_L02_A4_176401_20210407_182209_20210407_190029_000.h5'
HEP4 = 'CSES_data/CSES_01_HEP_4_L02_A4_202091_20210923_184621_20210923_192441_000.h5'
LAP1 = 'CSES_data/CSES_01_LAP_1_L02_A3_174201_20210324_070216_20210324_073942_000.h5'
SCM1 = 'CSES_data/CSES_01_SCM_1_L02_A2_183380_20210523_154551_20210523_162126_000.h5'
HEPD = 'CSES_data/CSES_HEP_DDD_0219741_20220117_214156_20220117_230638_L3_0000267631.h5'

file_list = [EFD1, HEP1, HEP4, LAP1, SCM1, HEPD]

def dataset(path):
    return xarray.open_dataset(path, engine = 'h5netcdf', phony_dims = 'sort')

def variables(data):
    return list(data.keys())

# %%
CSES_DATA_TABLE = {'EFD':{'1':'ULF','2':'ELF','3':'VLF','4':'HF'},\
                   'HPM':{'1':'FGM1','2':'FGM2','3':'CDSM','5':'FGM1Hz'},\
                   'SCM':{'1':'ULF','2':'ELF','3':'VLF'},\
                   'LAP':{'1':'50mm', '2':'10mm'},\
                   'PAP':{'0':''}, \
                   'HEP':{'1':'P_L','2':'P_H','3':'D','4':'P_X'}}

# splits file name

def parse_filename(filename):

    fl_list = filename[10:].split('_')
    out={}
    if len(filename[10:]) == 66:
        out['Satellite'] = fl_list[0]+fl_list[1]
        out['Instrument'] = fl_list[2]
        try:
            out['Data Product'] = CSES_DATA_TABLE[fl_list[2]][fl_list[3]]
        except:
            out['Data Product'] = 'Unknown' 
        out['Instrument No.'] = fl_list[3]
        out['Data Level'] = fl_list[4]
        out['orbitn'] = fl_list[6]
        out['year'] = fl_list[7][0:4]
        out['month'] = fl_list[7][4:6]
        out['day'] = fl_list[7][6:8]
        out['time'] = fl_list[8][0:2]+':'+fl_list[8][2:4]+':'+fl_list[8][4:6]
        out['t_start'] = datetime(int( out['year']),int(out['month']),int(out['day']),\
                            int(fl_list[8][0:2]),int(fl_list[8][2:4]),int(fl_list[8][4:6])) 
        out['t_end'] = datetime(int(fl_list[9][0:4]),int(fl_list[9][4:6]),int(fl_list[9][6:8]),\
                            int(fl_list[10][0:2]),int(fl_list[10][2:4]),int(fl_list[10][4:6]))
    elif len(filename[10:]) == 69:
        out['Satellite'] = fl_list[0]+'_01'
        out['Instrument'] = fl_list[1]
        out['Data Product'] = fl_list[2]
        out['Data Level'] = fl_list[-2]
        out['orbitn'] = fl_list[3]
        out['year'] = fl_list[4][0:4]
        out['month'] = fl_list[4][4:6]
        out['day'] = fl_list[4][6:8]
        out['time'] = fl_list[5][0:2]+':'+fl_list[5][2:4]+':'+fl_list[5][4:6]
        out['t_start'] = datetime(int( out['year']),int(out['month']),int(out['day']),\
                            int(fl_list[5][0:2]),int(fl_list[5][2:4]),int(fl_list[5][4:6])) 
        out['t_end'] = datetime(int(fl_list[6][0:4]),int(fl_list[6][4:6]),int(fl_list[6][6:8]),\
                            int(fl_list[7][0:2]),int(fl_list[7][2:4]),int(fl_list[7][4:6]))

    return out

# %%
def polygon(points, data):
    
    ds = dataset(data)

    geo_lat = ds.GEO_LAT
    geo_lon = ds.GEO_LON

    max_latitude = points[0][1]
    min_longitude = points[0][0]
    min_latitude = points[2][1]
    max_longitude = points[2][0]

    lat_mask = (geo_lat >= min_latitude) & (geo_lat <= max_latitude)
    lon_mask = (geo_lon >= min_longitude) & (geo_lon <= max_longitude)

    final_mask = lat_mask + lon_mask

    filtered_subset = ds.where(final_mask, drop=True)

    if filtered_subset.GEO_LAT.size > 0 and filtered_subset.GEO_LON.size > 0:
        return(filtered_subset)

pts = [
    [70, 80],
    [10, 60],
    [10, 60],
    [10, 60],
    [70, 80]
]

polygon(pts, EFD1)


