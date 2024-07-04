import streamlit as st

st.write("# Welcome to C.SEES! 👁️")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    C.SEES is an open-source app framework built specifically for analyzing and visualizing data from the CSES satellite.
    **👈 Select a demo from the sidebar** to see some examples of what C.SEES can do!
    ### Want to learn more?
    - Check out the [C.SEES documentation](https://cses.issibern.ch/)
    - Join the [C.SEES community](https://cses.issibern.ch/community)
    ### See more examples
    - Analyze the CSES satellite data using a neural network: [CSES Data Analysis with Neural Network](https://github.com/cses-issibern/csees-demo-neural-network)
    - Visualize the CSES satellite data on a map: [CSES Data Visualization on Map](https://github.com/cses-issibern/csees-demo-map)
"""
)
