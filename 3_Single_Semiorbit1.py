import streamlit as st
from parsing2.parsing import extract_dataset_type
from multiprocessing import Pool
import time
from parsing2.parsing import payload_filter, orbit_filter

from plotting.functions.plot_EFD import plot_EFD
from plotting.functions.plot_LAP import lap_plot
from plotting.functions.plot_HEPPX import heppx_plot

from plotting.functions.plot_SCM import scmplot
from plotting.functions.plot_HEPPH import plotheph
from plotting.functions.plot_HEPPD import plot_HEPD
from plotting.functions.paralleltest import paralleltest

try:
    filtered_files = st.session_state.filtered_files
except:
    st.warning('No filter found!', icon="⚠️")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])

with tab1:
   st.header("A cat")
   st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

with tab2:
   st.header("A dog")
   st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

filtered_files = st.session_state.filtered_files
search_bar = st.text_input("Insert orbit number", "",type="default", max_chars=6, help="Please enter only numbers")
orbit_paths = orbit_filter(filtered_files, search_bar)

option = st.multiselect(
"Instrument Type",
(" ", "EFD", "SCM", "LAP", "HEP_1", "HEP_4", "HEP_2", "HEP_DDD"))

dataset_type = extract_dataset_type(filtered_files)
print(dataset_type)
st.write(dataset_type)



st.divider()
selected_files = st.selectbox("Select Files", orbit_paths)

# if st.button("plot"):
#     if option:
#         for dataset in dataset_type:
#             file_path = dataset[0]
#             dataset_type = dataset[1]
#             for sensors in option:
#                 if dataset_type == 'EFD' == sensors:
#                     plot_EFD(file_path)
#                 elif dataset_type == 'LAP' == sensors:
#                     lap_plot(file_path)
#                 elif dataset_type == 'HEP_4' == sensors:
#                     heppx_plot(file_path)
#                 elif dataset_type == 'HEP_1' == sensors:
#                     st.write("working on function")
#                 elif dataset_type == 'SCM' == sensors:
#                     scmplot(file_path)
#                 elif dataset_type == 'HEP_2' == sensors:
#                     st.write("test")
#                     plotheph(file_path)
# min_lat, max_lat = calculate_extremes(coordinates)
# st.write(f"Leftmost Latitude: {min_lat:.6f}")
# st.write(f"Rightmost Latitude: {max_lat:.6f}")

if st.button("plot"):
    if option:
        # Initialize arrays for each sensor type
        efd_files = []
        lap_files = []
        hep4_files = []
        hep1_files = []
        scm_files = []
        hep2_files = []
        hep3_files = []
        args = []

        # Populate arrays based on selected datasets and sensors
        for dataset in dataset_type:
            file_path = dataset[0]
            dataset_type = dataset[1]
            
            for sensor in option:
                if dataset_type == 'EFD' and sensor == 'EFD':
                    efd_files.append(file_path)
                elif dataset_type == 'LAP' and sensor == 'LAP':
                    lap_files.append(file_path)
                elif dataset_type == 'HEP_4' and sensor == 'HEP_4':
                    hep4_files.append(file_path)
                elif dataset_type == 'HEP_1' and sensor == 'HEP_1':
                    hep1_files.append(file_path)
                elif dataset_type == 'SCM' and sensor == 'SCM':
                    scm_files.append(file_path)
                elif dataset_type == 'HEP_2' and sensor == 'HEP_2':
                    hep2_files.append(file_path)
                elif dataset_type == 'HEP_DDD' and sensor == 'HEP_DDD':
                    hep3_files.append(file_path)


        if(len(scm_files) > 1):
            for i in range(3):
                args.append((scm_files, 'SCM', i))
            # plot_sequential_SCM(scm_files)
            # aggregated_SCM_angles(scm_files)
            # aggregated_SCM_waveform(scm_files)
        elif(len(scm_files)==1):
            args.append((scm_files, 'SCM_s', 0))
            scmplot(scm_files)


        if(len(efd_files) > 1):
            for i in range(3):
                args.append((efd_files, 'EFD', i))
            # paralleltest(efd_files)
            # plot_sequential_EFD(efd_files)
            # aggregate_EFD_angles(efd_files)
            # aggregate_EFD_waveform(efd_files)
        elif(len(efd_files)==1):
            args.append((efd_files[0], 'EFD_s', 0))

            plot_EFD(efd_files, False)



        if(len(lap_files) > 1):
            for i in range(2):
                args.append((lap_files, 'LAP', i))
            # plot_sequential_LAP(lap_files)
            # aggregated_LAP_electron(lap_files)
        elif(len(lap_files)==1):
            args.append((lap_files[0], 'LAP_s', 0))
            lap_plot(lap_files[0])




        if(len(hep1_files) > 1):
            for i in range(2):
                args.append((hep1_files, 'HEPL', i))
            # plot_proton_electron_count_verse_time(hep1_files[0], False)
            # plot_sequential_HEPPL(hep1_files)
            # aggregated_HEPPL_electron_proton(hep1_files)
        elif(len(hep1_files)==1):
            args.append((hep1_files[0], 'HEPL_s', 0))
            #plot_hepl(hep1_files, False)




        if(len(hep2_files) > 1):
            for i in range(2):
                args.append((hep2_files, 'HEPH', i))
            # plot_sequential_HEPPH(hep2_files)
            # aggregated_HEPPH_electron_proton(hep2_files)
        elif(len(hep2_files)==1):
            args.append((hep2_files[0], 'HEPH_s', 0))
            plotheph(hep2_files[0])



        #FIX HEP_DDD (john)
        if(len(hep3_files) > 1):
            for i in range(2):
                args.append((hep3_files, 'HEPD', i))
            # plot_HEPD_multiple_files(hep3_files)
            # aggregate_HEPPD_electron_proton(hep3_files)
        elif(len(hep3_files)==1):
            args.append((hep3_files[0], 'HEPD', 0))
            # plot_HEPD(hep3_files[0])



        if(len(hep4_files) > 1):
            for i in range(2):
                args.append((hep4_files, 'HEPX', i))
            # plot_sequential_HEPPX(hep4_files)
            # aggregated_HEPPX_xray(hep4_files)
            # plot_HEPD_multiple_files(hep3_files)
        elif(len(hep4_files)==1):
            args.append((hep4_files[0], 'HEPX', 0))
            # heppx_plot(hep4_files[0])

    st.write(time.time())
    with Pool(8) as p:
        for fig in p.starmap(paralleltest, args):
            st.write(time.time())
            if isinstance(fig, tuple):
                for f in fig:
                    st.plotly_chart(f)
            else:
                st.plotly_chart(fig)
    st.write(time.time())