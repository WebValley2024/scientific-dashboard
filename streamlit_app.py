import streamlit as st

st.set_page_config(page_title="Data manager", page_icon="👁️")

DATA_DIR = "/home/grp2/grp2/scientific-dashboard/data/processed/metadata/"


filters = st.Page("1_Filters_Democopy.py", title="📈_Filters_Demo.py")
hello = st.Page("hello.py", title="hello")
plots = st.Page("2_Plotscopy.py", title="📊_Plots.py")
single_semiorbit = st.Page("3_Single_Semiorbit.py", title="🛰️_Single_Semiorbit.py")
multi_semiorbit = st.Page("multi.py", title="🛰️_Multi_Semiorbit.py")

pg = st.navigation(
    {
        "Home": [hello],
        "Tools": [filters],
        "Averaging plots": [plots],
        #"Single Semiorbit": [single_semiorbit],
        "Mutliple Semiorbits": [multi_semiorbit],
    })

pg.run()



