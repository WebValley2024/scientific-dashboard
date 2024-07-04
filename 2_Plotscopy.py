import os
import plotly as plt
import plotly.graph_objects as go
import streamlit as st
import xarray as xr
from settings import DATA_DIR
from filtering.filtering import (
    ascending_descending_filter,
    get_filenames_from_orbits,
    orbit_filter,
    payload_filter,
    return_coordinates,
    semiorbits_filter,
    semiorbits_payload_filter,
)

from plotting.functions.averaging import (
    plot_med_quantile,
    add_stats_trace,
    get_med_quantile,
)

from plotly.subplots import make_subplots
from plotting.functions.plot_LAP import plot_A311, plot_A321
from plotting.functions.plot_EFD import plot_A111_W, plot_A112_W, plot_A113_W
from plotting.functions.plot_HEPPD import plot_electron_LAT_D, plot_proton_LAT_D
from plotting.functions.plot_HEPPH import plot_electron_LAT_H, plot_proton_LAT_H
from plotting.functions.plot_HEPPL import plot_electron_LAT_L, plot_proton_LAT_L
from plotting.functions.plot_HEPPX import plot_XrayRate_LAT_X
from plotting.functions.plot_SCM import plot_A231_W, plot_A232_W, plot_A233_W
from settings import DATA_DIR

st.session_state.search = False
try:
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    st_map = st.session_state.st_map
except:
    st.warning("No filter found!", icon="⚠️")
    st.stop()


#the coordinates are returned from the map
selected_coordinates = return_coordinates(st_map)

#the coordinates are used to filter the semiorbits
filtered_orbits_df = semiorbits_filter(start_date, end_date, selected_coordinates)

# at this point filtered_orbits_df is a dataframe with the following columns:
# semiorbit_nr, start_time, end_time, geometry

filtered_files_df = get_filenames_from_orbits(filtered_orbits_df.semiorbit_nr)
# at this point filtered_files_df is a dataframe with the following columns:
# file_name, semiorbit_nr, payload
filtered_files_df["filepath"] = filtered_files_df.apply(
    lambda s: (DATA_DIR / s.payload / s.file_name).with_suffix(".zarr.zip"), axis=1
)

# at this point filtered_files_df is a dataframe with the following columns:
# file_name, semiorbit_nr, payload, filepath
st.session_state.filtered_files = filtered_files_df

if filtered_files_df.empty:
    st.warning("No files founded", icon="⚠️")
    st.stop()


# st.session_state.search = True if search_bar else False
payload = st.selectbox(
    "Instrument Type",
    ("EFD_ULF", "SCM", "LAP", "HEPP_L", "HEPP_H", "HEPD" "HEPP_X"),
    index=0,
)

sensors_multi_select = {
    "EFD_ULF": ["A111_W", "A112_W", "A113_W"],
    "SCM": ["A231_W", "A232_W", "A233_W"],
    "LAP": ["A311", "A321"],
    "HEPP_L": ["Count_Electron", "Count_Proton"],
    "HEPP_H": ["Count_Electron", "Count_Proton"],
    "HEPD": ["HEPD_ele_counts", "HEPD_pro_counts"],
    "HEPP_X": ["XrayRate"],
}

asc_des = st.radio("", ("Ascending", "Descending"), index=0)

sensors = st.multiselect(
    "Sensor Type", sensors_multi_select[payload], sensors_multi_select[payload]
)

if not payload and not sensors:
    st.warning("No filters applied!", icon="⚠️")
    st.stop()


st.divider()

search_bar = st.text_input(
    "Insert orbit number",
    "",
    type="default",
    max_chars=6,
    help="Please enter only numbers",
)



search_bar_files = semiorbits_payload_filter(payload, search_bar)

over_plot_file = st.selectbox("", search_bar_files, format_func=lambda filepath: os.path.basename(filepath))

st.divider()


st.write(filtered_files_df)
payload_filtered_files = filtered_files_df[filtered_files_df['payload']== payload]['filepath']
st.write("Payload filtered files", payload_filtered_files)
asc_des_filtered_files = ascending_descending_filter(payload_filtered_files, asc_des)

st.write("Acsending file", asc_des_filtered_files)
st.write(len(asc_des_filtered_files))

if len(asc_des_filtered_files) < 2:
    st.warning("No files within this filter", icon="⚠️")
    st.stop()


filelist = []
for p in asc_des_filtered_files:
    f = xr.open_zarr(p)
    try:
        f = f.rename({"Count_electron": "Count_Electron"})
        f = f.rename({"Count_proton": "Count_Proton"})
    except:
        pass
    filelist.append(f)

data_list = []
lat = f.GEO_LAT.values.flatten()

plotting_stuff = []

for sensor in sensors:
    data = f[sensor].values
    try:
        freq = data.shape[1]
    except:
        freq = 1
    data_list.append(freq)
    plotting_stuff.append(get_med_quantile(filelist, sensor))

plots = []

for i in range(len(sensors)):
    st.plotly_chart(plot_med_quantile(plotting_stuff[i], lat, data_list[i]))
    


payload_avg_functions = {
    "EFD_ULF": {"A111_W": plot_A111_W, "A112_W": plot_A112_W, "A113_W": plot_A113_W},
    "SCM": {"A231_W": plot_A231_W, "A232_W": plot_A232_W, "A233_W": plot_A233_W},
    "LAP": {"A311": plot_A311, "A321": plot_A321},
    "HEPP_L": {"Count_Electron": plot_electron_LAT_L, "Count_Proton": plot_proton_LAT_L},
    "HEPP_H": {"Count_Electron": plot_electron_LAT_H, "Count_Proton": plot_proton_LAT_H},
    "HEPD": {
        "HEPD_ele_counts": plot_electron_LAT_D,
        "HEPD_pro_counts": plot_proton_LAT_D,
    },
    "HEPP_X": {"XrayRate": plot_XrayRate_LAT_X},
}

if over_plot_file:
    for idx, s in enumerate(sensors):
        fig = go.Figure()
        st.write(sensor)
        func = payload_avg_functions[payload][s]
        fig_1 = func(fig, os.path.join(DATA_DIR, over_plot_file))
        fig_1 = add_stats_trace(plotting_stuff[idx], fig_1, median_name="Median")
        st.plotly_chart(fig_1)
