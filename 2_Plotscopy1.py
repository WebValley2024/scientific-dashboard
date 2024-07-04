
import streamlit as st
from functions import get_med_quantile, plot_med_quantile, orbit_selector, plotA311, plot_twin_timeline_verse_time, add_stats_trace

from filtering.filtering import search_files, payload_filter, ascending_descending_filter, orbit_filter
from plotting.functions1.plot_LAP import plotA311, plotA321
import xarray as xr
import os
import plotly.graph_objects as go
import plotly as plt
from plotly.subplots import make_subplots


filtered_files = None
st.session_state.search = False
try:
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    st_map = st.session_state.st_map
except:
    st.warning('No filter found!', icon="⚠️")
    st.stop()

    
filtered_files = search_files(st_map, start_date, end_date)

st.session_state.filtered_files = filtered_files
if(filtered_files == None):
    st.warning("No files founded", icon="⚠️")
    st.stop()




#st.session_state.search = True if search_bar else False
payload = st.selectbox("Instrument Type", ("EFD_1", "SCM_1", "LAP_1", "HEP_1", "HEP_2", "HEP_4"), index=2)
sensors_multi_select = {
    "EFD_1": ["A111_W", "A112_W", "A113_W"],
    "SCM_1": ["A231_W", "A232_W", "A233_W"],
    "LAP_1": ["A311", "A321"],
    "HEP_1": ["Count_Electron", "Count_Proton"],
    "HEP_4": ["XrayRate"],
    "HEP_2": ["Count_Electron", "Count_Proton"],
}

asc_des = st.radio("", ("Ascending", "Descending"),index=0)

sensors = st.multiselect("Sensor Type", sensors_multi_select[payload], sensors_multi_select[payload])

if not payload and not sensors:
    st.warning('No filters applied!', icon="⚠️")
    st.stop()

st.divider()

search_bar = st.text_input("Insert orbit number", "",type="default", max_chars=6, help="Please enter only numbers")
orbit_paths = orbit_selector(payload_filter(os.listdir("/home/fbk/wv24/LAP"), payload), search_bar)
orbit_paths = payload_filter(orbit_paths, payload)
selected_files = st.selectbox("Select Files", orbit_paths)

st.divider()

payload_filtered_files = payload_filter(filtered_files, payload)
# st.write("payload files: ",payload_filtered_files)
st.write("Ascending or Descending: ", asc_des)
asc_des_filtered_files = ascending_descending_filter(payload_filtered_files, asc_des)
st.write("Acsending file", asc_des_filtered_files)
st.write(len(asc_des_filtered_files))
if(len(asc_des_filtered_files)<2):
    st.warning("No files within this filter", icon="⚠️")
    st.stop()


filelist = []
for p in asc_des_filtered_files:
    f= xr.open_zarr(p)
    try:
        f=f.rename({"Count_electron":"Count_Electron"})
        f=f.rename({"Count_proton": "Count_Proton"})
    except:
        pass
    filelist.append(f)

data_list = []
lat = f.GEO_LAT.values.flatten()



plotting_stuff = []
if(asc_des_filtered_files == None):
    st.warning("No files founded", icon="⚠️")
    st.stop()

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
    plots.append(st.plotly_chart(plot_med_quantile(plotting_stuff[i], lat, data_list[i])))


# if selected_files:
#     for i in (range(len(sensors))):
#         if(payload == "EFD_1"):
            #plot 3
        # if(payload == "EFD_1"):

        # if(payload == "EFD_1"):



    # "EFD_1": ["A111_W", "A112_W", "A113_W"],
    # "SCM_1": ["A231_W", "A232_W", "A233_W"],
    # "LAP_1": ["A311", "A321"],
    # "HEP_1": ["Count_Electron", "Count_Proton"],
    # "HEP_4": ["XrayRate"],
    # "HEP_2": ["Count_Electron", "Count_Proton"],


# if selected_files:
#     for i in range(len(sensors)):
        
#         if i == 1:
#             fig1 = plotA311("/home/grp2/nicola-largher/bla/7DATI1/" + selected_files)
#         else:
#             fig1 = plotA321("/home/grp2/nicola-largher/bla/7DATI1/" + selected_files)
#         fig1 = add_stats_trace(plotting_stuff[i], fig1, median_name="Median")
#         st.plotly_chart(fig1)


if(st.button("Aggregated/Sequential Plotting")):
    st.switch_page("multi.py")

