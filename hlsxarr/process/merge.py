import pandas as pd
import xarray as xr
import numpy as np
from typing import List


def _merge(df: pd.DataFrame, da_list: List[xr.DataArray]) -> xr.Dataset:
    """
    Merge a list of DataArrays into a single Dataset.
    Args:
        df: DataFrame with columns 'sat_id' and 'tile_id'.
        da_list: List of DataArrays to merge.
    Returns:
        xr.Dataset: Merged Dataset.
    """
    single_sat: bool = len(df["sat_id"].unique()) == 1

    sat_tile_combinations = df[["sat_id", "tile_id"]].drop_duplicates()

    ds_list_to_concat = []
    for sat_id, tile_id in sat_tile_combinations.itertuples(index=False):
        sat_tile_da_list = []
        for da in da_list:
            if sat_id == da.attrs["sat_id"] and tile_id == da.attrs["tile_id"]:
                sat_tile_da_list.append(da)

        merged_ds = xr.merge(sat_tile_da_list)

        if not single_sat:
            value = 0 if sat_id == "L30" else 1
            merged_ds["SAT"] = (
                ("time"),
                np.full(merged_ds.time.shape, value, dtype=np.uint8),
            )
            merged_ds.attrs["sat_ids"] = "L30 : 0, L15 : 1"

        merged_ds.attrs.pop("sat_id")
        merged_ds.attrs.pop("tile_id")
        merged_ds["time"].encoding["dtype"] = "float64"

        for var in merged_ds.data_vars:
            merged_ds[var] = (
                merged_ds[var].astype(np.uint8)
                if var == "FMASK"
                else merged_ds[var].astype(np.int16)
            )
        ds_list_to_concat.append(merged_ds)

    final_ds = xr.concat(ds_list_to_concat, dim="time").sortby("time")

    return final_ds
