import streamlit as st

st.set_page_config(page_title="Data manager", page_icon="👁️")

DATA_DIR = "/home/fbk/wv24/LAP"


filters = st.Page("1_Filters_Democopy1.py", title="📈_Select_Filters")
hello = st.Page("hello1.py", title="Spectra")
plots = st.Page("2_Plotscopy1.py", title="📊_Plot_Statistics")
single_semiorbit = st.Page("3_Single_Semiorbit1.py", title="🛰️_Single_Semiorbit")
multi = st.Page("multi.py", title="🛰️_Multiple_Semiorbits")


pg = st.navigation(
    {
        "Home": [hello],
        "Tools": [filters],
        "Averaging plots": [plots],
        "Single Semiorbit": [single_semiorbit],
        "Multiple Page": [multi],
    })

pg.run()



