
import streamlit as st
from plotting.functions.plot_EFD import plot_EFD
from plotting.functions.plot_EFD import aggregate_EFD_angles
from plotting.functions.plot_EFD import aggregate_EFD_waveform
from plotting.functions.plot_sequential_EFD import plot_sequential_EFD
# from plotting.functions.plot_EFD_merged import plot_EFD

from plotting.functions.plot_LAP import lap_plot
from plotting.functions.plot_LAP import aggregated_LAP_electron
from plotting.functions.LAP_Mul_plot_Final import plot_sequential_LAP

from plotting.functions.plot_SCM import scmplot
from plotting.functions.plot_SCM import aggregated_SCM_angles
from plotting.functions.plot_SCM import aggregated_SCM_waveform
from plotting.functions.plot_sequential_SCM import plot_sequential_SCM

from plotting.functions.plot_HEPPL import plot_hepl
from plotting.functions.plot_sequential_HEPPL import plot_sequential_HEPPL
from plotting.functions.plot_HEPPL import aggregated_HEPPL_electron_proton

from plotting.functions.plot_HEPPH import plotheph
from plotting.functions.plot_HEPPH import aggregated_HEPPH_electron_proton
from plotting.functions.HEPPH_MUL_plot import plot_sequential_HEPPH

from plotting.functions.HEPD_V2_fixed import plot_HEPPD
from plotting.functions.HEPPD_Mul_plot import plot_HEPD_multiple_files
from plotting.functions.plot_HEPPD import plot_HEPD
from plotting.functions.plot_HEPPD import aggregate_HEPPD_electron_proton

from plotting.functions.plot_HEPPX import heppx_plot
from plotting.functions.plot_sequential_HEPPX import plot_sequential_HEPPX
from plotting.functions.plot_HEPPX import aggregated_HEPPX_xray

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