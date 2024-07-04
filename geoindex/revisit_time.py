import glob
from pathlib import Path

import contextily as ctx
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt
from shapely.geometry import LineString, Point, shape, box

from tqdm import tqdm
from parsing import parse_filename
import os
import datetime

def process_file(
    path, min_lon, max_lon, min_lat, max_lat, lat_divisions, lon_divisions
):
    df = pd.read_csv(path)
    df = df.dropna()
    df = df[df.Lat.between(min_lat, max_lat) & df.Lon.between(min_lon, max_lon)]
    
    lon_step = (max_lon - min_lon) / lon_divisions
    lat_step = (max_lat - min_lat) / lat_divisions

    # def get_grid_position(lon, lat, min_lon, min_lat, lon_step, lat_step):
    #     lat_index = int((lat - min_lat) / lat_step)
    #     lon_index = int((lon - min_lon) / lon_step)
    #     return lat_index, lon_index

    df["lat_index"] = ((df.Lat - min_lat) / lat_step).astype(int)
    df["lon_index"] = ((df.Lon - min_lon) / lon_step).astype(int)

    return df


# file_paths = [
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027321_20180731_233412_20180801_001019_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027330_20180801_001744_20180801_005841_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027331_20180801_010513_20180801_014503_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027340_20180801_015228_20180801_022940_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027341_20180801_023956_20180801_031710_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027350_20180801_032712_20180801_040447_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027351_20180801_041440_20180801_045154_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027360_20180801_050156_20180801_054218_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027360_20180801_051057_20180801_051057_000.csv",
#     "../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/CSES_01_EFD_1_L02_A1_027361_20180801_054924_20180801_062638_000.csv"
# ]

file_paths = glob.glob(
    "/home/grp2/grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/*csv"#"../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/*csv"
)

def extract_dates(file_name):
    from datetime import datetime as dt

    try:
        base_name = os.path.basename(file_name) #returns the final component of a pathname
        parts = base_name.split('_')
        
        #find the index of the part that contains the start_date
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8:  # find the part with data format YYYYMMDD
                start_index = i
                break
        
        if start_index is None:
            raise ValueError(f"Formato data non trovato nel nome del file: {file_name}")
        
        start_date_str = '_'.join(parts[start_index:start_index + 2]) 
        end_date_str = '_'.join(parts[start_index + 2:start_index + 4])  
        
        start_date = dt.strptime(start_date_str, '%Y%m%d_%H%M%S').date()
        end_date = dt.strptime(end_date_str, '%Y%m%d_%H%M%S').date()
        
        return start_date, end_date
    except ValueError as e:
        print(f"Errore nel parsing delle date per il file {file_name}: {e}")
        return None, None
    

"""
for example 
file_paths = glob.glob(
    "/home/grp2/grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/*csv"#"../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/*csv"
)

or filter file_paths with check_Date_interval as in 
file_paths = glob.glob(
    "/home/grp2/grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/*csv"#"../../../grp2/scientific-dashboard/data/processed/metadata/EFD_ULF/*csv"
)
file_paths = check_Date_interval(file_paths, datetime.date(2018, 1,1),datetime.date(2019, 1,1))
"""
def get_dataframe(file_paths, LON_DIVISIONS = 36, LAT_DIVISIONS = 18):
    all_grid_dfs = []
    MIN_LAT = -75
    MAX_LAT=75
    MIN_LON = -175
    MAX_LON = 180
    for file_path in tqdm(file_paths):
        grid_df = process_file(
            file_path,
            min_lat=MIN_LAT,
            max_lat=MAX_LAT,
            min_lon=MIN_LON,
            max_lon=MAX_LON,
            lat_divisions=LAT_DIVISIONS,
            lon_divisions=LON_DIVISIONS,
        )
        parsed = parse_filename(file_path)
        grid_df['orbit_number']=parsed["semiorbit_nr"]
        all_grid_dfs.append(grid_df)

        combined_grid_df = pd.concat(all_grid_dfs, ignore_index=True)
        combined_grid_df['UTCTime'] = pd.to_datetime(combined_grid_df['UTCTime'], errors='coerce')
        return combined_grid_df



"""
examples for calling:
#orbit_aggregation, cell_aggregation, diff = lambda g: g.max() - g.min(), "min", False # -> minimum duration of passage through cell
#orbit_aggregation, cell_aggregation, diff = lambda g: g.max() - g.min(), "max", False # -> maximum duration of passage through cell
orbit_aggregation, cell_aggregation, diff = "median", "median", True # -> median time till satellite revisites a cell
#orbit_aggregation, cell_aggregation, diff = lambda g: g.max() - g.min(), "med", False # -> maximum duration of passage through cell


revisit_times_df = get_revisit_times(
    combined_grid_df,
    orbit_aggregation=orbit_aggregation,
    cell_aggregation=cell_aggregation,
    diff=diff
)
"""
def get_revisit_times(
    combined_grid_df, orbit_aggregation="median", cell_aggregation="median", diff=False
):
    def get_orbit_agg_time(combined_grid_df, lat, lon, aggregation="median"):
        specific_lat_index = lat
        specific_long_index = lon
        filtered_df = combined_grid_df[
            (combined_grid_df["lat_index"] == specific_lat_index)
            & (combined_grid_df["lon_index"] == specific_long_index)
        ]
        avg_utc_times = (
            filtered_df.groupby("orbit_number")
            .UTCTime.agg(aggregated=aggregation)
            .reset_index()
        )

        return avg_utc_times

    def get_revisit_time(
        combined_grid_df,
        lat,
        lon,
        orbit_aggregation="median",
        cell_aggregation="median",
        diff=False
    ):
        # median_times = get_orbit_agg_time(
        #     combined_grid_df, lat, lon, aggregation=orbit_aggregation
        # )
        # median_times["time_diff"] = median_times["aggregated"].sort_values().diff()
        # median_times = median_times.dropna(subset=["time_diff"])
        # revisit_time = median_times["time_diff"].agg(
        #     [cell_aggregation]
        # )  # .agg(['max'])#.agg(['median'])#.reset_index()
        # assert len(revisit_time) == 1
        # return revisit_time.iloc[0]

        aggregated = get_orbit_agg_time(
            combined_grid_df, lat, lon, orbit_aggregation
        ).aggregated
        if diff:
            aggregated = aggregated.sort_values().diff().dropna()

        res = aggregated.agg(cell_aggregation)

        return res

    revisit_times = []
    unique_positions = combined_grid_df[["lat_index", "lon_index"]].drop_duplicates()
    for _, row in unique_positions.iterrows():
        lat = row["lat_index"]
        lon = row["lon_index"]
        revisit_time = get_revisit_time(
            combined_grid_df,
            lat,
            lon,
            orbit_aggregation=orbit_aggregation,
            cell_aggregation=cell_aggregation,
            diff=diff
        )
        revisit_times.append(
            {"lat_index": lat, "lon_index": lon, "revisit_time": revisit_time}
        )
    revisit_times_df = pd.DataFrame(revisit_times)
    return revisit_times_df



def check_Date_interval(files_path, start_date_selector, end_date_selector):
    files_list = []
    for file in files_path:
        print(file)
        start_date, end_date = extract_dates(file)
        if(start_date_selector <= end_date and end_date_selector >= start_date):
            files_list.append(file)

    return files_list



"""
takes as input the output of get_revisit_times, what to divide the seconds in that frame to (by default converted
to hours) and the title for the colorbar
"""
def plot_revisit_times(revisit_times_df, convert = 3600, title = ""):
        # Convert the timedelta objects to numeric (e.g., hours)
    revisit_times_df["revisit_time"] = (
        revisit_times_df["revisit_time"].dt.total_seconds() / convert)  # Convert to hours
    table_complete = revisit_times_df.pivot(columns="lat_index", index="lon_index", values="revisit_time")#.fillna(0)
    plt.figure(figsize=(10, 6))
    plt.imshow(table_complete.T, cmap='Spectral', origin='lower')
    plt.colorbar(label=title)
    plt.xlabel('Longitude Index')
    plt.ylabel('Latitude Index')
    plt.title('Point Distribution in Grid')
    plt.show()

def plot_revisit_times_on_map(revisit_times_copy, convert = 3600, title = "", LON_DIVISIONS = 36, LAT_DIVISIONS = 18):
    MIN_LON, MAX_LON = -175, 180
    MIN_LAT, MAX_LAT = -75, 75
    lon_step = (MAX_LON - MIN_LON) / LON_DIVISIONS
    lat_step = (MAX_LAT - MIN_LAT) / LAT_DIVISIONS

    geometries = [
        box(
            MIN_LON + lon_index * lon_step,
            MIN_LAT + lat_index * lat_step,
            MIN_LON + (lon_index + 1) * lon_step,
            MIN_LAT + (lat_index + 1) * lat_step,
        )
        for lat_index, lon_index in zip(revisit_times_copy["lat_index"], revisit_times_copy["lon_index"])
    ]
    revisit_times_copy["revisit_time"] = (
            revisit_times_copy["revisit_time"].dt.total_seconds() / convert)  # Convert to hours
    gdf = gpd.GeoDataFrame(revisit_times_copy, geometry=geometries, crs="EPSG:4326")

    # Plot the grid cell densities on a map
    fig, ax = plt.subplots(figsize=(15, 5))
    gdf.to_crs(epsg=3857).plot(
        # gdf.plot(
        column="revisit_time",
        ax=ax,
        legend=True,
        cmap="Spectral",
        edgecolor="black",
        linewidth=0.5,
        alpha=0.5,
    )

    ctx.add_basemap(
        ax,
        zoom=2,
        source=ctx.providers.OpenStreetMap.Mapnik,
        # crs=gdf.crs,
    )  # Use another provider
    fig.suptitle(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    return fig