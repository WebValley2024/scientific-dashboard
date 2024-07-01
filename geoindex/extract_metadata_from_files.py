import glob
import os
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import xarray as xr
from tqdm import tqdm

# files = sorted(glob.glob("/disks/wd3/**/*h5", recursive=True))
# files = sorted(glob.glob("/disks/wv24/**/*zarr.zip", recursive=True))
files = sorted(glob.glob("/home/fbk/wv24/**/*zarr.zip", recursive=True))
len(files)


outfolder = Path("../data/processed/metadata/")
outfolder.mkdir(exist_ok=True)


def stat_finder(fname, outfolder):
    try:
        folder, name = os.path.split(fname)
        # keep only the last level (payload name)
        base, folder = os.path.split(folder)
        if folder.startswith("20"):
            folder = os.path.split(base)[1]

        if name.endswith(".h5"):
            fname_id = name.replace(".h5", "")
        elif name.endswith(".zarr.zip"):
            fname_id = name.replace(".zarr.zip", "")
        else:
            raise ValueError(f"Unrecognized file extension: {name}")

        outfname = outfolder / folder / f"{fname_id}.csv"
        if outfname.exists():
            return None

        # ds = xr.open_dataset(fname)
        ds = xr.open_zarr(fname)

        if "LonLat" in ds.var():
            df = pd.DataFrame(ds.LonLat.values, columns=["Lon", "Lat"])
        elif "GEO_LAT" in ds.var() and "GEO_LON" in ds.var():
            df = pd.DataFrame(
                {"Lon": ds.GEO_LON.values.flatten(), "Lat": ds.GEO_LAT.values.flatten()}
            )

        # get the time dimensione, which can be called either "UTCTime" or "UTC_TIME"
        if "UTCTime" in ds.var():
            time_dim = "UTCTime"
        elif "UTC_TIME" in ds.var():
            time_dim = "UTC_TIME"
        else:
            raise ValueError("Time dimension not found (tried UTCTime and UTC_TIME)")

        df["UTCTime"] = pd.to_datetime(
            pd.Series(ds[time_dim].values.flatten()).map(str).str.ljust(17, "0"),
            format="%Y%m%d%H%M%S%f",
        )

        outfname.parent.mkdir(exist_ok=True, parents=True)

        df.to_csv(outfname, index=False)
        ds.close()
    except Exception as e:
        print(e)
        return (fname, e)


n_workers = 32
pool = Pool(n_workers)

errors = []

for e in tqdm(
    pool.imap_unordered(partial(stat_finder, outfolder=outfolder), files),
    total=len(files),
):
    pass
