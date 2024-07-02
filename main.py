import streamlit as st
from streamlit_navigation_bar import st_navbar
from Integratedxar import draw_map

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'  # Default to home page

# Sidebar for navigation

selected_page = st_navbar(["Home", "Documentation", "Examples",])

match selected_page:
        case "Home":
            st.session_state['page'] = 'home'
        case "Documentation":
            st.session_state['page'] = 'documentation'
        case "Examples":
            st.session_state['page'] = 'examples'
        # If an exact match is not confirmed, this last case will be used if provided
        case _:
            raise ValueError(f"Unknown page: {selected_page}")

# Display the selected page
if st.session_state['page'] == 'home':
    draw_map()
elif st.session_state['page'] == 'documentation':
    st.write("One File")
elif st.session_state['page'] == 'examples':
    st.write("Multiple Files")
else:
    raise ValueError(f"Unknown page: {st.session_state['page']}")


