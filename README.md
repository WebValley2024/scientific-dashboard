# Installation

## Prerequisites
1. **Python Installation**: Ensure you have Python installed on your system (Python 3.6 or later).
2. **Git Installation**: Ensure you have Git installed on your system.
3. **Streamlit Installation**: Ensure Streamlit is installed. If not, you can install it using `pip`.


### 1. Clone the GitHub Repository

Open your command line interface (CLI) and clone the repository using the `git clone` command. Replace `<repository-url>` with the actual URL of the GitHub repository.
```bash
git clone <repository-url>
```

### 2. Navigate to the Repository Directory

Change your directory to the floned repository folder.

```bash
cd repository 
```

### 3. Install the Dependencies

Install the required dependencies using: 

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit script

Run the script named ` ` using the Streamlit CLI command:

```bash 
streamlit run app.py
```

### 5. Access the Application in Browser

After running the command, Streamlit will start a local server and provide you with a URL (usually http://localhost:8501). Open this URL in your web browser to access your Streamlit application.


## Dependencies

``` python
import os
from glob import glob
import datetime
import folium
import geopandas as gpd
import h5py
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
import xarray as xr
from folium.plugins import Draw
from plotly.subplots import make_subplots
from scipy.stats import skew, kurtosis, t
from shapely import geometry
import streamlit as st
from streamlit_folium import st_folium
 
from plotting.functions.plot_EFD import plot_EFD
# from plotting.functions.plot_EFD_merged import plot_EFD
from plotting.functions.plot_LAP import lap_plot
from plotting.functions.plot_LAP import aggregated_LAP_electron
from plotting.functions.plot_HEPPX import heppx_plot
from plotting.functions.plot_SCM import scmplot
from plotting.functions.plot_SCM import aggregated_SCM_angles
from plotting.functions.plot_SCM import aggregated_SCM_waveform
from plotting.functions.plot_sequential_SCM import plot_sequential_SCM
from plotting.functions.plot_sequential_EFD import plot_sequential_EFD
from plotting.functions.plot_sequential_HEPPL import plot_sequential_HEPPL
from plotting.functions.plot_sequential_HEPPX import plot_sequential_HEPPX
from plotting.functions.HEPPH_MUL_plot import plot_sequential_HEPPH
from plotting.functions.HEPD_V2_fixed import plot_HEPPD
from plotting.functions.HEPPD_Mul_plot import plot_HEPD_multiple_files
from plotting.functions.LAP_Mul_plot_Final import plot_sequential_LAP
# from plotting.functions.HEPPL_Mul_plot import plosequential_HEPPL
# from plotting.functions.plot_sequential_HEPPL import plot_proton_electron_count_verse_time
from plotting.functions.plot_HEPPL import plot_proton_electron_count_verse_time
from plotting.functions.plot_HEPPH import plotheph
from plotting.functions.plot_HEPPD import plot_HEPD
from plotting.functions.plot_HEPPL import plot_hepl
```
# Dashboard

(TO DO)


# Payloads

| Instrument | Data file | Variables |
|-|-|-|
| EFD | ULF electric waveform / power spectrum | magnetic field waveform and power spectrum density (PSD) |
| SCM | ULF waveform / PSD | electric field waveform and power spectrum density (PSD) |
| LAP | 50mm electron temeprature and density of the ball detecting | electron density, electron temeprature |
| HEPP-L | low energetic particle flux and spectrum | electron and proton pitch angle spectrum |
| HEPP-H | high energetic particle flux and spectrum | electron and proton flux and spectrum |
| HEPD | energetic particle flux and spectrum | electron and proton flux and spectrum |
| HEPP-X | X-ray flux and spectrum | x-ray flux and energy spectrum |

------------------------------------------------------------

## Electron Field Detector (EFD)

**Overview:**
This module provides functions to visualize and analyze electromagnetic field data (EFD) using Streamlit, Plotly, and various other scientific libraries. The primary functionality includes plotting waveforms, power spectra, and aggregate angle data from EFD datasets.

**Functions:**

1. **plot_EFD(path)**
    - **Parameters:**
        - `path` (str): The path to the EFD dataset (either in Zarr or NetCDF format).
    - **Returns:**
        - `fig1` (plotly.graph_objs.Figure): Figure showing X, Y, Z waveforms and the vector sum.
        - `fig2` (plotly.graph_objs.Figure): Figure showing polar and azimuthal angles.
    - **Details:**
        - Opens the dataset and extracts relevant data.
        - Computes the magnitude and angles from the waveform data.
        - Reduces the frequency of the data for more efficient plotting.
        - Creates and configures interactive Plotly figures for:
            - X, Y, Z waveforms and their vector sum.
            - Polar and azimuthal angles.
            - Power spectra for each axis.
        - Displays the figures in a Streamlit app.

2. **aggregate_EFD_angles(files, angle_type='polar')**
    - **Parameters:**
        - `files` (list of str): List of paths to EFD datasets.
        - `angle_type` (str): The type of angle to plot ('polar' or 'azimuth').
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Figure showing the selected angle type versus geographic latitude.
    - **Details:**
        - Iterates over the provided files, extracting and computing the required angles.
        - Reduces the frequency of the data for more efficient plotting.
        - Plots the selected angle against geographic latitude for each dataset.
        - Configures and returns a Plotly figure.

3. **aggregate_EFD_waveform(files, waveform_type='X')**
    - **Parameters:**
        - `files` (list of str): List of paths to EFD datasets.
        - `waveform_type` (str): The type of waveform to plot ('X', 'Y', 'Z', or 'vector').
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Figure showing the selected waveform type versus geographic latitude.
    - **Details:**
        - Iterates over the provided files, extracting and computing the required waveforms.
        - Reduces the frequency of the data for more efficient plotting.
        - Plots the selected waveform against geographic latitude for each dataset.
        - Configures and returns a Plotly figure.

**Example Usage:**

```python
import streamlit as st

# Path to the dataset
path = 'path_to_your_dataset.zarr'

# Plot and display EFD data
fig1, fig2 = plot_EFD(path)
st.plotly_chart(fig1)
st.plotly_chart(fig2)

# Aggregate and plot angles from multiple datasets
files = ['file1.zarr', 'file2.zarr']
angle_fig = aggregate_EFD_angles(files, angle_type='polar')
st.plotly_chart(angle_fig)

# Aggregate and plot waveforms from multiple datasets
waveform_fig = aggregate_EFD_waveform(files, waveform_type='X')
st.plotly_chart(waveform_fig)
```

### Notes:

- Ensure the data files are accessible and correctly formatted (Zarr or NetCDF).
- Adjust the frequency reduction parameter in reduce_frequency as needed for your data.
- The module assumes specific variable names in the datasets (A111_W, A112_W, A113_W, etc.). Modify the code if your dataset uses different naming conventions.
-----------------------------------------------------------------
## Langmuir Probe (LAP)

**Overview:**
This module provides functions to visualize and analyze electron density and temperature data from Langmuir Probe (LAP) datasets using Streamlit, Plotly, and xarray. The primary functionality includes plotting twin timelines for electron density and temperature versus time, and mapping electron density and temperature against geographic coordinates.

**Functions:**

1. **plot_twin_timeline_verse_time(fig, path)**
    - **Parameters:**
        - `fig` (plotly.graph_objs.Figure): The Plotly figure object to which the traces will be added.
        - `path` (str): The path to the LAP dataset (either in Zarr or NetCDF format).
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Updated Plotly figure object.
    - **Details:**
        - Opens the dataset and extracts verse time, electron density, and electron temperature data.
        - Reduces the frequency of the data for more efficient plotting.
        - Removes the first element of the data and verse time to avoid anomalies.
        - Extends the verse time for proper plotting and creates twin y-axes for density and temperature.
        - Configures and returns the Plotly figure with appropriate axis titles and logarithmic scaling.

2. **plot_twin_timeline_utc(fig, path)**
    - **Parameters:**
        - `fig` (plotly.graph_objs.Figure): The Plotly figure object to which the traces will be added.
        - `path` (str): The path to the LAP dataset (either in Zarr or NetCDF format).
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Updated Plotly figure object.
    - **Details:**
        - Opens the dataset and extracts UTC time, electron density, and electron temperature data.
        - Converts the extracted time data to UTC format.
        - Reduces the frequency of the data for more efficient plotting.
        - Removes the first element of the data and UTC time to avoid anomalies.
        - Extends the UTC time for proper plotting and creates twin y-axes for density and temperature.
        - Configures and returns the Plotly figure with appropriate axis titles and logarithmic scaling.

3. **plot_on_map_density(fig, path)**
    - **Parameters:**
        - `fig` (plotly.graph_objs.Figure): The Plotly figure object to which the trace will be added.
        - `path` (str): The path to the LAP dataset (either in Zarr or NetCDF format).
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Updated Plotly figure object.
    - **Details:**
        - Opens the dataset and extracts latitude, longitude, and electron density data.
        - Reduces the frequency of the data for more efficient plotting.
        - Extends the latitude and longitude data for proper plotting.
        - Configures the Plotly figure with a geographic scatter plot, color-coded by electron density.
        - Sets up the layout with a geographic projection and appropriate color scale.

4. **plot_on_map_temperature(fig, path)**
    - **Parameters:**
        - `fig` (plotly.graph_objs.Figure): The Plotly figure object to which the trace will be added.
        - `path` (str): The path to the LAP dataset (either in Zarr or NetCDF format).
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Updated Plotly figure object.
    - **Details:**
        - Opens the dataset and extracts latitude, longitude, and electron temperature data.
        - Reduces the frequency of the data for more efficient plotting.
        - Extends the latitude and longitude data for proper plotting.
        - Configures the Plotly figure with a geographic scatter plot, color-coded by electron temperature.
        - Sets up the layout with a geographic projection and appropriate color scale.

5. **lap_plot(f_path)**
    - **Parameters:**
        - `f_path` (str): The path to the LAP dataset file.
    - **Returns:**
        - None. The function directly updates the Streamlit app with the plots.
    - **Details:**
        - Creates a 2x2 grid layout in Streamlit.
        - Plots electron density and temperature timelines and geographic maps in separate subplots.
        - Displays the plots in the Streamlit app.

6. **aggregated_LAP_electron(files, variable='A311')**
    - **Parameters:**
        - `files` (list of str): List of paths to LAP dataset files.
        - `variable` (str): The variable to plot ('A311' for electron density or 'A321' for electron temperature). Default is 'A311'.
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Plotly figure object containing the aggregated data plot.
    - **Details:**
        - Iterates over the provided files, extracting latitude and the specified variable data.
        - Reduces the frequency of the data for more efficient plotting.
        - Aggregates the data and plots it against latitude.
        - Configures and returns a Plotly figure with appropriate titles and layout.

**Example Usage:**

```python
import streamlit as st

# Single file path input
path = 'path_to_your_dataset.zarr'
if path:
    lap_plot(path)

# Multiple file paths input
files = ['file1.zarr', 'file2.zarr']
if files:
    variable = st.selectbox("Select variable to plot:", ["A311", "A321"])
    fig = aggregated_LAP_electron(files, variable)
    st.plotly_chart(fig)
```

### Notes:

- Ensure the data files are accessible and correctly formatted (Zarr or NetCDF).
- Adjust the frequency reduction parameter in reduce_frequency as needed for your data.
- The module assumes specific variable names in the datasets (A311, A321, etc.). Modify the code if your dataset uses different naming conventions.
-----------------------------------------------------------------

## Search-Coil Magnetometer

**Overview:**
This module provides functions to visualize and analyze magnetic field data (SFD) using Streamlit, Plotly, and various scientific libraries. The primary functionality includes plotting waveforms, power spectra, and aggregate angle data from SFD datasets.

**Functions:**

1. **plot_SCM(path, multiple)**
    - **Parameters:**
        - `path` (str): The path to the SFD dataset (either in Zarr or NetCDF format).
        - `multiple` (bool): Whether to plot power spectra for multiple components.
    - **Returns:**
        - `fig1` (plotly.graph_objs.Figure): Figure showing X, Y, Z waveforms, and the vector sum.
        - `fig2` (plotly.graph_objs.Figure): Figure showing polar and azimuthal angles.
    - **Details:**
        - Opens the dataset and extracts relevant data.
        - Computes the magnitude and angles from the waveform data.
        - Reduces the frequency of the data for more efficient plotting.
        - Creates and configures interactive Plotly figures for:
            - X, Y, Z waveforms and their vector sum.
            - Polar and azimuthal angles.
            - Power spectra for each axis.
        - Displays the figures in a Streamlit app.

2. **plot_SCM_on_map(data, latitude, longitude)**
    - **Parameters:**
        - `data` (xarray.DataArray): The field data to be plotted.
        - `latitude` (xarray.DataArray): Latitude coordinates.
        - `longitude` (xarray.DataArray): Longitude coordinates.
    - **Returns:**
        - None
    - **Details:**
        - Flattens the data and coordinates.
        - Computes the logarithm of the magnitude data for better visualization.
        - Extends the coordinates to match the frequency of data points.
        - Creates a scatter plot on a world map using Plotly and GeoPandas.
        - Displays the figure in a Streamlit app.

3. **scmplot(file_path)**
    - **Parameters:**
        - `file_path` (str): Path to the SFD file.
    - **Returns:**
        - None
    - **Details:**
        - Opens the dataset and extracts latitude, longitude, and waveform data.
        - Reduces the frequency of the waveforms.
        - Computes the magnitude of the field data.
        - Calls `plot_SCM_on_map` to plot the data on a map.
        - Calls `plot_SCM` to plot waveforms and spectra.

4. **aggregated_SCM_waveform(files, component='A231_W')**
    - **Parameters:**
        - `files` (list of str): List of paths to SFD datasets.
        - `component` (str): The type of waveform to plot ('A231_W', 'A232_W', 'A233_W').
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Figure showing the selected waveform type versus geographic latitude.
    - **Details:**
        - Iterates over the provided files, extracting and computing the required waveforms.
        - Reduces the frequency of the data for more efficient plotting.
        - Plots the selected waveform against geographic latitude for each dataset.
        - Configures and returns a Plotly figure.

5. **aggregated_SCM_angles(files, angle_type='polar')**
    - **Parameters:**
        - `files` (list of str): List of paths to SFD datasets.
        - `angle_type` (str): The type of angle to plot ('polar' or 'azimuthal').
    - **Returns:**
        - `fig` (plotly.graph_objs.Figure): Figure showing the selected angle type versus geographic latitude.
    - **Details:**
        - Iterates over the provided files, extracting and computing the required angles.
        - Reduces the frequency of the data for more efficient plotting.
        - Plots the selected angle against geographic latitude for each dataset.
        - Configures and returns a Plotly figure.

**Example Usage:**

```python
import streamlit as st

# Path to the dataset
path = 'path_to_your_dataset.zarr'

# Plot and display SFD data
fig1, fig2 = plot_SCM(path, multiple=False)
st.plotly_chart(fig1)
st.plotly_chart(fig2)

# Aggregate and plot angles from multiple datasets
files = ['file1.zarr', 'file2.zarr']
angle_fig = aggregated_SCM_angles(files, angle_type='polar')
st.plotly_chart(angle_fig)

# Aggregate and plot waveforms from multiple datasets
waveform_fig = aggregated_SCM_waveform(files, component='A231_W')
st.plotly_chart(waveform_fig)
```

### Notes:

-	Ensure the data files are accessible and correctly formatted (Zarr or NetCDF).
- Adjust the frequency reduction parameter in reduce_frequency as needed for your data.
- The module assumes specific variable names in the datasets (‘A231_W’, ‘A232_W’, ‘A233_W’, etc.). Modify the code if your dataset uses different naming conventions.

-----------------------------------------------------------------

## High-Energy Particle Packages (HEPPD, HEPPL, HEPPH, HEPPX)

### Overview
This module contains several plotting functions to visualize data from Zarr files. The functions are designed to plot electron and proton counts, energy spectrums, and pitch angles against time or geographical coordinates. The module uses libraries such as xarray, numpy, pandas, plotly, matplotlib, and streamlit for data manipulation and visualization.

### Functions

### `plot_proton_electron_count_verse_time(path, multiple)`
Plots electron and proton counts against verse time.

#### Parameters
- `path` (str): Path to the Zarr file.
- `multiple` (bool): If True, returns the plotly figure without displaying it in Streamlit.

#### Returns
- `fig` (plotly.graph_objects.Figure): Plotly figure object.

#### Details
- Flattens the data (`data` and `data2`) and coordinates (`verse_time`).
- Computes the logarithm of the magnitude data (`data` and `data2`) for better visualization.
- Extends the coordinates (`verse_time`) to match the frequency of data points.
- Creates a scatter plot with two y-axes (for electron and proton counts) on a shared x-axis (`verse time`) using Plotly (`go.Scatter`) and Plotly Subplots (`make_subplots`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_proton_electron_count_utc(path)`
Plots electron and proton counts against UTC time.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Flattens the data (`data` and `data2`) and coordinates (`verse_time`).
- Computes the logarithm of the magnitude data (`data` and `data2`) for better visualization.
- Extends the coordinates (`verse_time`) to match the frequency of data points.
- Creates a scatter plot with two y-axes (for electron and proton counts) on a shared x-axis (`verse time`) using Plotly (`go.Scatter`) and Plotly Subplots (`make_subplots`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_on_map_electron_count(path)`
Plots electron counts on a geographical map.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches latitude (`latitude`) and longitude (`longitude`) coordinates from the data (`f`).
- Flattens the count data (`measure`) and coordinates (`lon`, `lat`).
- Extends the longitude and latitude coordinates to match the frequency of data points.
- Creates a scatter plot on a world map using GeoPandas (`go.Scattergeo`) and Plotly.
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_on_map_proton_count(path)`
Plots proton counts on a geographical map.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches latitude (`latitude`) and longitude (`longitude`) coordinates from the data (`f`).
- Flattens the count data (`measure`) and coordinates (`lon`, `lat`).
- Extends the longitude and latitude coordinates to match the frequency of data points.
- Creates a scatter plot on a world map using GeoPandas (`go.Scattergeo`) and Plotly.
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_electron_energy_verse(path)`
Plots electron energy spectrum against verse time.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches verse time (`verse_time`) and energy data (`data`) from the input file (`f`).
- Sums the energy data along the third axis.
- Sets a threshold (`threshold`) for near-zero values in the data.
- Creates a heatmap of electron energy spectrum over verse time using Plotly (`go.Heatmap`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_electron_energy_utc(path)`
Plots electron energy spectrum against UTC time.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches UTC time (`verse_time`) and energy data (`data`) from the input file (`f`).
- Sums the energy data along the third axis.
- Sets a threshold (`threshold`) for near-zero values in the data.
- Converts the verse time data to UTC time format using `pd.to_datetime`.
- Creates a heatmap of electron energy spectrum over UTC time using Plotly (`go.Heatmap`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_electron_pitch_verse(path)`
Plots electron pitch angle against verse time.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches verse time (`verse_time`) and pitch angle (`f.PitchAngle`) data from the input file (`f`).
- Sums the data along the second axis (pitch angle).
- Creates a heatmap of electron pitch angle over verse time using Plotly (`go.Heatmap`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_proton_energy_verse(path)`
Plots proton energy spectrum against verse time.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches verse time (`verse_time`) and energy data (`data`) from the input file (`f`).
- Sums the energy data along the second axis.
- Computes the logarithm of the energy data (`data`) for better visualization.
- Creates a heatmap of proton energy spectrum over verse time using Plotly (`go.Heatmap`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_proton_energy_utc(path)`
Plots proton energy spectrum against UTC time.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches UTC time (`verse_time`) and energy data (`data`) from the input file (`f`).
- Sums the energy data along the second axis.
- Computes the logarithm of the energy data (`data`) for better visualization.
- Converts the verse time data to UTC time format using `pd.to_datetime`.
- Creates a heatmap of proton energy spectrum over UTC time using Plotly (`go.Heatmap`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

---

### `plot_proton_pitch_verse(path)`
Plots proton pitch angle against verse time.

#### Parameters
- `path` (str): Path to the Zarr file.

#### Returns
- None

#### Details
- Fetches verse time (`verse_time`) and pitch angle (`f.PitchAngle`) data from the input file (`f`).
- Sums the data along the second axis (pitch angle).
- Creates a heatmap of proton pitch angle over verse time using Plotly (`go.Heatmap`).
- Displays the figure in a Streamlit app using `st.plotly_chart`.

## Usage
To use these functions, import the module and call the desired function with the path to the Zarr file. Example:

```python
import plotting_module

path = "path/to/zarr/file.zarr"
plotting_module.plot_proton_electron_count_verse_time(path, multiple=False)

```
### Notes
- Ensure the data files are accessible and correctly formatted (Zarr or NetCDF).
- Adjust the frequency reduction parameter in reduce_frequency as needed for your data.
- The module assumes specific variable names in the datasets (‘A231_W’, ‘A232_W’, ‘A233_W’, etc.). Modify the code if your dataset uses different naming conventions.