import xarray as xr
import gradio as gr
import pandas as pd

def load_and_display_data(file_path):
    try:
        # Load the dataset using xarray with the h5netcdf engine
        data = xr.open_dataset(file_path, engine='h5netcdf', phony_dims='sort')

        # Prepare dataset info
        dataset_info = {
            "Variable": list(data.data_vars),
            "Dimensions": [str(var.dims) for var in data.data_vars.values()],
            "Shape": [var.shape for var in data.data_vars.values()],
            "Data Type": [var.dtype for var in data.data_vars.values()],
        }
        dataset_df = pd.DataFrame(dataset_info)

        # Extract a small subset of the data
        subset = data.isel(phony_dim_0=slice(0, 18))
        subset_info = {
            "Variable": list(subset.data_vars),
            "Dimensions": [str(var.dims) for var in subset.data_vars.values()],
            "Shape": [var.shape for var in subset.data_vars.values()],
            "Data Type": [var.dtype for var in subset.data_vars.values()],
        }
        # subset_df = pd.DataFrame(subset_info)
        # subset_df = subset.to_dataframe()[['Altitude', 'GMLonLat']]
        subset_df = subset.to_dataframe()


        # Extract values from the subset for display
        subset_values = subset[['Altitude', 'GMLonLat']].to_dataframe().head(20).to_markdown()
        

        return dataset_df, subset_df, subset_values
    except Exception as e:
        # Return the error message in case of exception
        return str(e), str(e), ""

# Define the Gradio interface
def on_file_upload(file):
    if file is not None:
        dataset_df, subset_df, subset_values = load_and_display_data(file.name)
        return dataset_df, subset_df, subset_values
    else:
        return None, None, None

with gr.Blocks() as demo:
    gr.Markdown("### HDF5 Dataset Viewer")
    
    with gr.Row():
        file_input = gr.File(label="Upload HDF5 file")

    dataset_info_output = gr.DataFrame(label="Dataset Info")
    subset_info_output = gr.DataFrame(label="Subset Info")
    subset_values_output = gr.Markdown(label="Subset Values")

    file_input.upload(on_file_upload, [file_input], [dataset_info_output, subset_info_output, subset_values_output])

demo.launch(share=True)
