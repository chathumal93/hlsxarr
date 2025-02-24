import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from .stac2xrda import _stac2xrda
from ..roi import RoiPolygon
import xarray as xr
from typing import List


def _read(
    roi: RoiPolygon,
    df: pd.DataFrame,
    workers: int,
    edl_token: str,
) -> List[xr.DataArray]:
    """"""
    logging.basicConfig(level=logging.INFO)
    logging.info("Reading HLS data from STAC API...")

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The 'df' argument must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("The input DataFrame is empty.")

    # Store successful reads
    data_arrays = []
    fails = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []

        # Set up the tqdm progress bar
        with tqdm(
            total=len(df), desc="Reading HLS Data", unit="file", ncols=80
        ) as pbar:
            for _, row in df.iterrows():
                futures.append(
                    executor.submit(
                        _stac2xrda,
                        roi.geometry,
                        edl_token,
                        row["stac_url"],
                        row["date"],
                        row["sat_id"],
                        row["tile_id"],
                        row["band"],
                    )
                )

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if isinstance(
                        result, xr.DataArray
                    ):  # Confirm result is a valid xarray
                        pbar.update(1)
                        data_arrays.append(result)
                    else:
                        fails += 1
                except Exception as exc:
                    logging.error(f"Exception occurred during reading: {exc}")
                    fails += 1

    return data_arrays
