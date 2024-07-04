import os
from glob import glob
import datetime
import folium
import geopandas as gpd
import h5py
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
import xarray as xr
from folium.plugins import Draw
from plotly.subplots import make_subplots
from scipy.stats import skew, kurtosis, t
from shapely import geometry
import streamlit as st
from streamlit_folium import st_folium
from multiprocessing import Pool

import time

from func.plot_EFD import plot_EFD
from func.plot_EFD import aggregate_EFD_angles
from func.plot_EFD import aggregate_EFD_waveform
from func.plot_sequential_EFD import plot_sequential_EFD
# from func.plot_EFD_merged import plot_EFD

from func.plot_LAP import lap_plot
from func.plot_LAP import aggregated_LAP_electron
from func.LAP_Mul_plot_Final import plot_sequential_LAP

from func.plot_SCM import scmplot
from func.plot_SCM import aggregated_SCM_angles
from func.plot_SCM import aggregated_SCM_waveform
from func.plot_sequential_SCM import plot_sequential_SCM

from func.plot_HEPPL import plot_hepl
from func.plot_sequential_HEPPL import plot_sequential_HEPPL
from func.plot_HEPPL import aggregated_HEPPL_electron_proton

from func.plot_HEPPH import plotheph
from func.plot_HEPPH import aggregated_HEPPH_electron_proton
from func.HEPPH_MUL_plot import plot_sequential_HEPPH

from func.HEPD_V2_fixed import plot_HEPPD
from func.HEPPD_Mul_plot import plot_HEPD_multiple_files
from func.plot_HEPPD import plot_HEPD
from func.plot_HEPPD import aggregate_HEPPD_electron_proton

from func.plot_HEPPX import heppx_plot
from func.plot_sequential_HEPPX import plot_sequential_HEPPX
from func.plot_HEPPX import aggregated_HEPPX_xray

# from func.HEPPL_Mul_plot import plosequential_HEPPL
# from func.plot_sequential_HEPPL import plot_proton_electron_count_verse_time

if not st.session_state.filtered_files:
    st.stop()

filtered_files = st.session_state.filtered_files

#REPLACE
folder_path = '/home/grp2/dhruva-sharma/scientific-dashboard/webappfiles/data/concat'
folder_path = '/home/wvuser/cses_personal_data'
def dataset(path):

    try:
        ds = xr.open_zarr(path)
        return ds
    except Exception as e:
        ds = xr.open_dataset(path, engine='h5netcdf', phony_dims='sort')
        return ds
 
# Function to list all variable names in a dataset
def variables(data):
    return list(data.keys())

# Function to calculate leftmost and rightmost latitude extremes

def extract_dates(file_name):
    from datetime import datetime as dt

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
        
        start_date = dt.strptime(start_date_str, '%Y%m%d_%H%M%S').date()
        end_date = dt.strptime(end_date_str, '%Y%m%d_%H%M%S').date()
        
        return start_date, end_date
    except ValueError as e:
        print(f"Errore nel parsing delle date per il file {file_name}: {e}")
        return None, None
    
# Function for map drawing
def draw_map():
    dataset_type = extract_dataset_type(filtered_files)
    print(dataset_type)
    st.write(dataset_type)

    option = st.multiselect(
        "Instrument Type",
        (" ", "EFD", "SCM", "LAP", "HEP_1", "HEP_4", "HEP_2", "HEP_DDD"))
    
    if st.button("plot"):
        if option:
            efd_files = []
            lap_files = []
            hep4_files = []
            hep1_files = []
            scm_files = []
            hep2_files = []
            hep3_files = []
            args = []

            for dataset in dataset_type:
                file_path = dataset[0]
                dataset_type = dataset[1]
                
                for sensor in option:
                    if dataset_type == 'EFD' and sensor == 'EFD':
                        efd_files.append(file_path)
                    elif dataset_type == 'LAP' and sensor == 'LAP':
                        lap_files.append(file_path)
                    elif dataset_type == 'HEP_4' and sensor == 'HEP_4':
                        hep4_files.append(file_path)
                    elif dataset_type == 'HEP_1' and sensor == 'HEP_1':
                        hep1_files.append(file_path)
                    elif dataset_type == 'SCM' and sensor == 'SCM':
                        scm_files.append(file_path)
                    elif dataset_type == 'HEP_2' and sensor == 'HEP_2':
                        hep2_files.append(file_path)
                    elif dataset_type == 'HEP_DDD' and sensor == 'HEP_DDD':
                        hep3_files.append(file_path)

                

            if(len(scm_files) > 1):
                for i in range(3):
                    args.append((scm_files, 'SCM', i))
                # plot_sequential_SCM(scm_files)
                # aggregated_SCM_angles(scm_files)
                # aggregated_SCM_waveform(scm_files)
            elif(len(scm_files)==1):
                args.append((scm_files, 'SCM_s', 0))
                # scmplot(scm_files)


            if(len(efd_files) > 1):
                for i in range(3):
                    args.append((efd_files, 'EFD', i))
                # paralleltest(efd_files)
                # plot_sequential_EFD(efd_files)
                # aggregate_EFD_angles(efd_files)
                # aggregate_EFD_waveform(efd_files)
            elif(len(efd_files)==1):
                args.append((efd_files[0], 'EFD_s', 0))

                # plot_EFD(efd_files, False)
            # st.write("before appending")
            # st.write(time.time())
            if(len(lap_files) > 1):
                for i in range(2):
                    args.append((lap_files, 'LAP', i))
                # plot_sequential_LAP(lap_files)
                # aggregated_LAP_electron(lap_files)
            elif(len(lap_files)==1):
                args.append((lap_files[0], 'LAP_s', 0))
                # lap_plot(lap_files[0])
            # st.write("after appending")
            # st.write(time.time())



            if(len(hep1_files) > 1):
                for i in range(2):
                    args.append((hep1_files, 'HEPL', i))
                # plot_proton_electron_count_verse_time(hep1_files[0], False)
                # plot_sequential_HEPPL(hep1_files)
                # aggregated_HEPPL_electron_proton(hep1_files)
            elif(len(hep1_files)==1):
                args.append((hep1_files[0], 'HEPL_s', 0))
                # plot_hepl(hep1_files, False)




            if(len(hep2_files) > 1):
                for i in range(2):
                    args.append((hep2_files, 'HEPH', i))
                # plot_sequential_HEPPH(hep2_files)
                # aggregated_HEPPH_electron_proton(hep2_files)
            elif(len(hep2_files)==1):
                args.append((hep2_files[0], 'HEPH_s', 0))
                # plotheph(hep2_files[0])



            #FIX HEP_DDD (john)
            if(len(hep3_files) > 1):
                for i in range(2):
                    args.append((hep3_files, 'HEPD', i))
                # plot_HEPD_multiple_files(hep3_files)
                # aggregate_HEPPD_electron_proton(hep3_files)
            elif(len(hep3_files)==1):
                args.append((hep3_files[0], 'HEPD', 0))
                # plot_HEPD(hep3_files[0])



            if(len(hep4_files) > 1):
                for i in range(2):
                    args.append((hep4_files, 'HEPX', i))
                # plot_sequential_HEPPX(hep4_files)
                # aggregated_HEPPX_xray(hep4_files)
                # plot_HEPD_multiple_files(hep3_files)
            elif(len(hep4_files)==1):
                args.append((hep4_files[0], 'HEPX', 0))
                # heppx_plot(hep4_files[0])

        st.write("Start ", time.time())
        start = time.time()
        # st.write(start)
        for arg in args:
            fig = paralleltest(*arg)
            # st.write("done processing")
            # st.write(time.time())
            if isinstance(fig, tuple):
                st.write(time.time())
                for f in fig:
                    st.plotly_chart(f)
            else:
                st.plotly_chart(fig)
            # st.write("done plotting")
            # st.write(time.time())
        total = time.time() - start
        st.write("Done processing & plotting")
        st.write("Took ", total, " seconds")

def extract_dataset_type(file_paths):    
    dataset_types = []
    
    for file_path in file_paths:
        file_name = file_path.split('/')[-1]
        
        if 'EFD' in file_name:
            dataset_types.append([file_path, 'EFD'])
        elif 'LAP' in file_name:
            dataset_types.append([file_path, 'LAP'])
        elif 'SCM' in file_name:
            dataset_types.append([file_path, 'SCM'])
        elif 'HEP_4' in file_name:
            dataset_types.append([file_path, 'HEP_4'])
        elif 'HEP_1' in file_name:
            dataset_types.append([file_path, 'HEP_1'])
        elif 'HEP_2' in file_name:
            dataset_types.append([file_path, 'HEP_2'])
        elif 'HEP_DDD' in file_name:
            dataset_types.append([file_path, 'HEP_DDD'])
        else:
            raise ValueError(f"Unknown dataset type in file name: {file_name}")
    return dataset_types

def paralleltest(file_path, sensor, i):
    if sensor == 'EFD':
        st.write("efd")
        if(i == 0):
            return aggregate_EFD_angles(file_path)
        elif(i == 1):
            return aggregate_EFD_waveform(file_path)
        elif(i == 2):
            return plot_sequential_EFD(file_path)
    elif sensor == "SCM":
        st.write("scm")
        if(i == 0):
            return plot_sequential_SCM(file_path)
        elif(i == 1):
            return aggregated_SCM_angles(file_path)
        elif(i == 2):
            return aggregated_SCM_waveform(file_path)
    elif sensor == "LAP":
        st.write("scm")
        if(i == 0):
            return plot_sequential_LAP(file_path)
        elif(i == 1):
            return aggregated_LAP_electron(file_path)
    elif sensor == "HEPL":
        st.write("hepl")
        if(i == 0):
            return plot_sequential_HEPPL(file_path)
        elif(i == 1):
            return aggregated_HEPPL_electron_proton(file_path)
    elif sensor == "HEPH":
        st.write("heph")
        if(i == 0):
            return plot_sequential_HEPPH(file_path)
        elif(i == 1):
            return aggregated_HEPPH_electron_proton(file_path)
    elif sensor == "HEPD":
        st.write("hepd")
        if(i == 0):
            return plot_HEPD_multiple_files(file_path)
        elif(i == 1):
            return aggregate_HEPPD_electron_proton(file_path)
    elif sensor == "HEPX":
        if(i == 0):
            return plot_sequential_HEPPX(file_path)
        elif(i == 1):
            return aggregated_HEPPX_xray(file_path)
                
# Main function 
def main():
    st.title("Map Drawing and Statistical Analysis Tool")
    draw_map()
    # statistical_analysis()



main()
    

