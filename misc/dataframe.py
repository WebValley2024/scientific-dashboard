import os
import geopandas as gpd
import pandas as pd
from datetime import datetime, timezone
import h5py
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import xarray as xr
import xarray
from shapely import geometry
from glob import glob


project_dir = "./CSES_files"

EFD1 = 'CSES_01_EFD_1_L02_A1_213330_20211206_164953_20211206_172707_000.h5'
HEP1 = 'CSES_01_HEP_1_L02_A4_176401_20210407_182209_20210407_190029_000.h5'
HEP4 = 'CSES_01_HEP_4_L02_A4_202091_20210923_184621_20210923_192441_000.h5'
LAP1 = 'CSES_01_LAP_1_L02_A3_174201_20210324_070216_20210324_073942_000.h5'
SCM1 = 'CSES_01_SCM_1_L02_A2_183380_20210523_154551_20210523_162126_000.h5'
HEPD = 'CSES_HEP_DDD_0219741_20220117_214156_20220117_230638_L3_0000267631.h5'

file_list = [
    os.path.join(project_dir, EFD1),
    os.path.join(project_dir, HEP1),
    os.path.join(project_dir, HEP4),
    os.path.join(project_dir, LAP1),
    os.path.join(project_dir, SCM1),
    os.path.join(project_dir, HEPD)
]

def extract_dates(file_name):
    try:
        base_name = os.path.basename(file_name) #returns the final component of a pathname
        parts = base_name.split('_')
        
        #find the index of the part that contains the start_date
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8:  # find the part with data format YYYYMMDD
                start_index = i
                break
        
        if start_index is None:
            raise ValueError(f"Formato data non trovato nel nome del file: {file_name}")
        
        start_date_str = '_'.join(parts[start_index:start_index + 2]) 
        end_date_str = '_'.join(parts[start_index + 2:start_index + 4])  
        
        start_date = datetime.strptime(start_date_str, '%Y%m%d_%H%M%S')
        end_date = datetime.strptime(end_date_str, '%Y%m%d_%H%M%S')
        
        return start_date, end_date
    except ValueError as e:
        print(f"Errore nel parsing delle date per il file {file_name}: {e}")
        return None, None
    

def extract_orbit(file_name):
    try:
        base_name = os.path.basename(file_name)
        parts = base_name.split('_')
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8: 
                start_index = i
                break
    
        if start_index is None:
            raise ValueError(f"Formato data non trovato nel nome del file: {file_name}")
        
        orbit = parts[start_index - 1]  
        return orbit
    except ValueError as e:
        print(f"Errore nel parsing dell'orbita per il file {file_name}: {e}")
        return None
    

def parse_filename(file_name):
    start_date, end_date = extract_dates(file_name)
    semiorbit_nr = extract_orbit(file_name)
    return {
        'file_name': file_name,
        "start_date": start_date, 
        "end_date" : end_date,
        "semiorbit_nr": semiorbit_nr
    }

data = []

for file in file_list:
    metadata = parse_filename(file)
    if metadata:
        data.append(metadata)
    #metadata["semiorbit_nr"]
    #semiorbits_geo[metadata["semiorbit_nr"]]
    # {
    #     "start_date": ...
    #     "start_date": ...
    #     "start_date": ...
    # }
if data:
    columns = list(data[0].keys())
else:
    columns = []


df = pd.DataFrame(data, columns=columns)

df