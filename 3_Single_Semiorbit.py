import streamlit as st
from parsing.parsing import extract_dataset_type
from multiprocessing import Pool
import time
import os
import pandas as pd
from plotting.functions.plot_EFD import plot_EFD
from plotting.functions.plot_LAP import lap_plot
from plotting.functions.plot_HEPPX import heppx_plot
from plotting.functions.plot_HEPPL import plot_hepl

from plotting.functions.plot_SCM import scmplot
from plotting.functions.plot_HEPPH import plotheph
from plotting.functions.plot_HEPPD import plot_HEPD
from plotting.functions.paralleltest import paralleltest

from filtering.filtering import semiorbits_payload_filter, semi_orbit_into_map_filtered

try:
    filtered_files = st.session_state.filtered_files
except:
    st.warning('No filter found!', icon="⚠️")
    st.stop()

filtered_files = st.session_state.filtered_files

search_bar = st.text_input("Insert orbit number", "",type="default", max_chars=6, help="Please enter only numbers")


search_bar_files = semi_orbit_into_map_filtered(filtered_files, search_bar)

if search_bar_files.empty:
    st.warning("No files within this filters", icon="⚠️")
    st.stop()
else:
    st.write(search_bar_files)


search_bar_files_paths = search_bar_files[["payload", "filepath"]]
st.write(search_bar_files_paths)


payloads = st.multiselect(
    "Instrument Type",
    ("EFD_ULF", "SCM", "LAP", "HEPP_L", "HEPP_H", "HEPD" "HEPP_X"),
)


if st.button("Plot"):
    if payloads:
        for payload in payloads:
            file_paths = search_bar_files_paths[search_bar_files_paths["payload"] == payload]["filepath"]
            if not file_paths.empty:
                file_path = file_paths.iloc[0]  # Assuming you need the first match

                if payload == "EFD_ULF":
                    plot_EFD(file_path, False)
                elif payload == "SCM":
                    scmplot(file_path)
                elif payload == "LAP":
                    lap_plot(file_path)
                elif payload == "HEPP_L":
                    plot_hepl(file_path)
                elif payload == "HEPP_H":
                    plotheph(file_path)
                elif payload == "HEPD":
                    plot_HEPD(file_path)
                elif payload == "HEPP_X":
                    heppx_plot(file_path)
            else:
                st.warning(f"No file path found for payload: {payload}", icon="⚠️")
    else:
        st.warning("No filters applied!", icon="⚠️")
        st.stop()


st.divider()
