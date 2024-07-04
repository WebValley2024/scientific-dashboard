from glob import glob
import folium
import numpy as np
import pandas as pd
import seaborn as sns
from folium.plugins import Draw
from plotly.subplots import make_subplots
from scipy.stats import skew, kurtosis, t
import streamlit as st
from streamlit_folium import st_folium
import datetime
st.markdown("# Plotting Demo")
st.sidebar.header("Plotting Demo")

#progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
m = folium.Map(location=[45.5, -122.6], zoom_start=2, max_bounds=True)
draw = Draw(
    draw_options={
        'polyline': False,
        'polygon': True,
        'circle': False,
        'marker': False,
        'circlemarker': False,
        'rectangle': True,
    }
)
draw.add_to(m)
st_map = st_folium(m, width=1000, height=400)

col1, col2 = st.columns(2)
start_date = col1.date_input("Start date", datetime.date(2018, 2, 2))
end_date = col2.date_input("End date", value=datetime.date.today())


search = st.button("Search Files")
st.session_state.search = search
if search:
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date
    st.session_state.st_map = st_map
    st.switch_page("2_Plotscopy.py")

