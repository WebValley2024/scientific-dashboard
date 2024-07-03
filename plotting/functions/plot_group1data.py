import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
# Make a GET request to the specified URL

def parse_flux(flux_str):
    match = re.search(r"([a-zA-Z])(\d+\.\d+)", flux_str)
    if match:
        return match.group(1), float(match.group(2))
    return "", 0

def get_color(colorscale, value, vmin, vmax):
    normalized_value = (value - vmin) / (vmax - vmin)
    color = px.colors.sample_colorscale(colorscale, normalized_value)
    return color[0]

def get_catalogue_data(kind, start_date: str, stop_date: str):
    if kind not in ("earthquake", "grb", "tgf", "gms", "swe"):
        print("kind is not in a recognized format, if you empty data, check its value")

    url = f"http://192.168.90.183:8000/spadeapp/{kind}_json/?start={start_date}&end={stop_date}"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        print("Request was successful")
        # with open("earthquake_data.json", "w+") as f:
        #     f.write(response.content.decode("utf-8"))
        data = response.json()
        print(data)
    else:
        print("Request failed with status code:", response.status_code)
        data = None

    return data


# with open("earthquake_data.json", "r") as file:
#     data = json.load(file)


def plot_earthquake_data(data):
    # Extract relevant fields
    trigger_times = []
    magnitudes = []
    places = []

    for entry in data:
        fields = entry["fields"]
        trigger_times.append(fields["trigger_time"])
        magnitudes.append(fields["magnitude"])
        places.append(fields["place"])

    # Convert trigger_times to a suitable format
    trigger_times = pd.to_datetime(trigger_times)
    # Create a DataFrame from the extracted data
    df = pd.DataFrame(
        {"Trigger Time": trigger_times, "Magnitude": magnitudes, "Place": places}
    )

    # Create the plot
    fig = go.Figure()

    colorscale = px.colors.sequential.Viridis
    vmin, vmax = df['Magnitude'].min(), df['Magnitude'].max()

    for index, row in df.iterrows():
        color = get_color(colorscale, row['Magnitude'], vmin, vmax)
        fig.add_trace(
            go.Scatter(
                x=[row["Trigger Time"], row["Trigger Time"]],
                y=[0, 1],
                mode="lines",
                line=dict(
                    color=color,
                    width=2,
                ),
                showlegend=False,
                hoverinfo="text",
                text=f"Place: {row['Place']}<br>Magnitude: {row['Magnitude']}",
            )
        )

    # Update layout
    fig.update_layout(
        title="Earthquake Events Timeline",
        xaxis_title="Time",
        yaxis_title="",
        yaxis=dict(showticklabels=False),
        plot_bgcolor="white",
    )

    # Show the plot
    return fig


def plot_grb_data(data):
    trigger_times = []
    sigmas = []
    sources = []

    for entry in data:
        fields = entry['fields']
        trigger_times.append(fields['trigger_time'])
        sigmas.append(float(fields['sigma']) if fields['sigma'] else 0)
        sources.append(fields['sat_source'])

    # Convert trigger_times to a suitable format
    trigger_times = pd.to_datetime(trigger_times)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame({
        'Trigger Time': trigger_times,
        'Sigma': sigmas,
        'Source': sources
    })

    # Create the plot
    fig = go.Figure()

    colorscale = px.colors.sequential.Viridis

    for index, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['Trigger Time'], row['Trigger Time']],
            y=[0, 1],
            mode='lines',
            line=dict(
                    color="red",
                    width=2,
                ),
            showlegend=False,
            hoverinfo='text',
            text=f"Source: {row['Source']}<br>Sigma: {row['Sigma']}"
        ))

    # Add color bar
    colorbar_trace = go.Scatter(
        x=[None], 
        y=[None], 
        mode='markers', 
        marker=dict(
            colorscale=colorscale, 
            showscale=True, 
            cmin=df['Sigma'].min(), 
            cmax=df['Sigma'].max(),
            colorbar=dict(
                title='Sigma',
                titleside='right'
            )
        ),
        hoverinfo='none'
    )
    fig.add_trace(colorbar_trace)

    # Update layout
    fig.update_layout(
        title='GRB Events Timeline',
        xaxis_title='Time',
        yaxis_title='',
        yaxis=dict(showticklabels=False),
        plot_bgcolor='white'
    )

    # Show the plot
    return fig


def plot_tgf_data(data):
    trigger_times = []
    sources = []

    for entry in data:
        fields = entry['fields']
        trigger_times.append(fields['trigger_time'])
        sources.append(fields['sat_source'])

    # Convert trigger_times to a suitable format
    trigger_times = pd.to_datetime(trigger_times)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame({
        'Trigger Time': trigger_times,
        'Source': sources
    })

    # Create the plot
    fig = go.Figure()

    colorscale = px.colors.sequential.Viridis

    for index, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['Trigger Time'], row['Trigger Time']],
            y=[0, 1],
            mode='lines',
            line=dict(
                    color="red",
                    width=2,
                ),
            showlegend=False,
            hoverinfo='text',
            text=f"Source: {row['Source']}"
        ))

    # Add color bar
    colorbar_trace = go.Scatter(
        x=[None], 
        y=[None], 
        mode='markers', 
        marker=dict(
            colorscale=colorscale, 
            showscale=True, 
        ),
        hoverinfo='none'
    )
    fig.add_trace(colorbar_trace)

    # Update layout
    fig.update_layout(
        title='TGF Events Timeline',
        xaxis_title='Time',
        yaxis_title='',
        yaxis=dict(showticklabels=False),
        plot_bgcolor='white'
    )

    # Show the plot
    return fig

def plot_swe_data(data):
    trigger_times = []
    fluxes = []
    flux_letters = []
    sources = []

    for entry in data:
        fields = entry['fields']
        trigger_times.append(fields['trigger_time'])
        letter, value = parse_flux(fields['flux']) if fields['flux'] else ("", 0)
        flux_letters.append(letter)
        fluxes.append(value)
        sources.append(fields['sat_source'])

    # Convert trigger_times to a suitable format
    trigger_times = pd.to_datetime(trigger_times)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame({
        'Trigger Time': trigger_times,
        'Flux': fluxes,
        'Flux Letter': flux_letters,
        'Source': sources
    })

    # Create the plot
    fig = go.Figure()

    colorscale = px.colors.sequential.Viridis

    for index, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['Trigger Time'], row['Trigger Time']],
            y=[0, 1],
            mode='lines',
            line=dict(
                    color=px.colors.sample_colorscale(colorscale, row['Flux'] / df['Flux'].max())[0],
                    width=2,
                ),
            showlegend=False,
            hoverinfo='text',
            text=f"Source: {row['Source']}<br>Flux: {row['Flux Letter']}{row['Flux']}"
        ))

    # Add color bar
    colorbar_trace = go.Scatter(
        x=[None], 
        y=[None], 
        mode='markers', 
        marker=dict(
            colorscale=colorscale, 
            showscale=True, 
            cmin=df['Flux'].min(), 
            cmax=df['Flux'].max(),
            colorbar=dict(
                title='Flux',
                titleside='right'
            )
        ),
        hoverinfo='none'
    )
    fig.add_trace(colorbar_trace)

    # Update layout
    fig.update_layout(
        title='SWE Events Timeline',
        xaxis_title='Time',
        yaxis_title='',
        yaxis=dict(showticklabels=False),
        plot_bgcolor='white'
    )

    # Show the plot
    return fig

def plot_gms_data(data):
    trigger_times = []
    speeds = []

    for entry in data:
        fields = entry['fields']
        trigger_time = fields['trigger_time']
        speed = float(fields['speed']) if fields['speed'] else None

        if speed is not None:
            trigger_times.append(trigger_time)
            speeds.append(speed)

    # Convert trigger_times to a suitable format
    trigger_times = pd.to_datetime(trigger_times)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame({
        'Trigger Time': trigger_times,
        'Speed': speeds
    })

    # Sort DataFrame by Trigger Time (optional, depending on API response order)
    df = df.sort_values(by='Trigger Time')

    # Create the plot
    fig = go.Figure()

    # Add trace for speed measurements
    fig.add_trace(go.Scatter(
        x=df['Trigger Time'],
        y=df['Speed'],
        mode='lines+markers',
        line=dict(color='blue', width=2),
        marker=dict(size=8, color='blue', line=dict(width=1)),
        hovertemplate='<b>Speed</b>: %{y}<br><b>Time</b>: %{x}<extra></extra>',
        name='Speed'
    ))

    # Update layout
    fig.update_layout(
        title='GMS Speed Measurements',
        xaxis_title='Time',
        yaxis_title='Speed',
        plot_bgcolor='white'
    )

    # Show the plot
    return fig

def plot_group1_data(kind, start_date, end_date):
    data = get_catalogue_data(kind, start_date, end_date)
    if kind=="earthquake":
        plot_earthquake_data(data)
    elif kind=="grb":
        plot_grb_data(data)
    elif kind=="gms":
        plot_gms_data(data)
    elif kind=="tgf":
        plot_tgf_data(data)
    elif kind=="swe":
        plot_swe_data(data)

