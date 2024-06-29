import gradio as gr
import pypistats
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
pd.options.plotting.backend = "plotly"

def get_data(lib, time):
    # Retrieve and process the data
    data = pypistats.overall(lib, total=True, format="pandas")
    data = data.groupby("category").get_group("with_mirrors").sort_values("date")
    start_date = date.today() - relativedelta(months=int(time.split(" ")[0]))
    df = data[(data['date'] > str(start_date))]

    # Plot the data
    fig = df.plot(x='date', y='downloads', title=f'{lib} Downloads Over the Last {time}')
    return fig

with gr.Blocks() as demo:
    with gr.Row():
        lib = gr.Dropdown(["pandas", "scikit-learn", "torch", "prophet"], label="Library", value="pandas")
        time = gr.Dropdown(["3 months", "6 months", "9 months", "12 months"], label="Downloads over the last...", value="12 months")

    plt = gr.Plot()

    lib.change(get_data, [lib, time], plt, queue=False)
    time.change(get_data, [lib, time], plt, queue=False)
    demo.load(get_data, [lib, time], plt, queue=False)

demo.launch()
