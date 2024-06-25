import gradio as gr
import xarray as xr

def get_data(lib, time):
    try:
        # Using h5netcdf engine with phony_dims parameter
        data = xr.open_dataset(
            'data/CSES_HEP_DDD_0219741_20220117_214156_20220117_230638_L3_0000267631.h5', 
            engine='h5netcdf', 
            phony_dims='sort'
        )
    except Exception as e:
        return str(e)
    
    # Convert the dataset to a DataFrame for easier handling and display
    df = data.to_dataframe().reset_index()
    
    # Filter data by the selected library (assuming there is a 'library' column)
    if 'library' in df.columns:
        df = df[df['library'] == lib].sort_values("date")
    
    # Filter data by the selected time period
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows where date conversion failed
    start_date = date.today() - relativedelta(months=int(time.split(" ")[0]))
    df = df[(df['date'] > str(start_date))]
    
    # Convert DataFrame to JSON for printing in Gradio
    data_json = df.to_json(orient='records')

    return data_json

with gr.Blocks() as demo:
    with gr.Row():
        lib = gr.Dropdown(["pandas", "scikit-learn", "torch", "prophet"], label="Library", value="pandas")
        time = gr.Dropdown(["3 months", "6 months", "9 months", "12 months"], label="Downloads over the last...", value="12 months")

    output = gr.Textbox()

    lib.change(get_data, [lib, time], output, queue=False)
    time.change(get_data, [lib, time], output, queue=False)
    demo.load(get_data, [lib, time], output, queue=False)

demo.launch()
