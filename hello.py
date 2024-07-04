import streamlit as st
 
st.write("# Welcome to Spectra! 👁️")
 
st.sidebar.success("Select a demo above.")
 
st.markdown(
    """
    Spectra is an open-source app framework built specifically for analyzing and visualizing data from the CSES satellite.
    **👈 Select a demo from the sidebar** to see some examples of what Spectra can do!
    ### Want to learn more?
    - Check out the [Spectra documentation](https://cses.issibern.ch/)
    - Join the [Spectra community](https://cses.issibern.ch/community)
    ### See more examples
    - Analyze the CSES satellite data using a neural network: [CSES Data Analysis with Neural Network](https://github.com/cses-issibern/csees-demo-neural-network)
    - Visualize the CSES satellite data on a map: [CSES Data Visualization on Map](https://github.com/cses-issibern/csees-demo-map)
"""
)