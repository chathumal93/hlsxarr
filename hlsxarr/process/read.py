import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from .stac2xrda import _stac2xrda
from ..roi import RoiPolygon
import xarray as xr
from typing import List
from ..exceptions import DataReadError


def _read(
    roi: RoiPolygon,
    df: pd.DataFrame,
    workers: int,
    edl_token: str,
) -> List[xr.DataArray]:
    """Read HLS data parallelly from the STAC API and return a list of xarray DataArrays.

    Args:
        roi (RoiPolygon): The region of interest.
        df (pd.DataFrame): The DataFrame containing the HLS data.
        workers (int): The number of workers to use.
        edl_token (str): The Earthdata Login token.

    Returns:
        List[xr.DataArray]: A list of xarray DataArrays.
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError("The 'df' argument must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("The input DataFrame is empty.")

    # Store successful reads
    data_arrays = []
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
                    if isinstance(result, xr.DataArray):
                        pbar.update(1)
                        data_arrays.append(result)
                    else:
                        raise DataReadError(
                            "Failed to read data. The result is not a DataArray."
                        )
                except Exception as e:
                    raise DataReadError(f"Failed to read data. {e}")

    return data_arrays
