import math
import requests
import time
import numpy as np
from rasterio.io import MemoryFile
from rasterio.windows import Window
from datetime import datetime
import xarray as xr
from typing import Optional
from ..utils import _get_projected_bounds, _get_roi_xr_utm_cordts, _get_bbox_utm_code
from .reproject import _reproject_xr_da
import threading


# Shared event to signal when to stop all threads
stop_event = threading.Event()


def _stac2xrda(
    roi: dict,
    token: str,
    url: str,
    dt: str,
    sat_id: str,
    tile_id: str,
    band: str,
) -> Optional[xr.DataArray]:
    """Read HLS data from the STAC API and return an xarray DataArray.

    Args:
        roi (dict): The region of interest.
        token (str): The Earthdata Login token.
        url (str): The STAC API URL.
        dt (str): The date and time of the data.
        sat_id (str): The satellite ID.
        tile_id (str): The tile ID.
        band (str): The band name.

    Returns:
        Optional[xr.DataArray]: An xarray DataArray.
    """

    retries = 5  # Maximum number of retries
    initial_delay = 1  # Initial delay (in seconds)
    max_delay = 32  # Maximum delay (in seconds)

    delay = initial_delay  # Start with the initial delay

    if stop_event.is_set():
        print(f"Skipping request for {url}")
        return None

    for attempt in range(retries):
        try:
            response = requests.get(
                url, headers={"Authorization": f"Bearer {token}"}, stream=True
            )
            response.raise_for_status()

            with MemoryFile(response.content) as memfile:
                with memfile.open() as dataset:
                    # Get the dataset metadata
                    transform = dataset.transform
                    img_width = dataset.width
                    img_height = dataset.height
                    img_crs = dataset.crs.to_string()
                    pixel_width = int(transform.a)
                    pixel_height = int(-transform.e)

                    # Get the ROI bounds in the image CRS.
                    minx, miny, maxx, maxy = _get_projected_bounds(roi, img_crs)
                    width = math.floor((maxx - minx) / pixel_width)
                    height = math.floor((maxy - miny) / pixel_height)

                    # Convert ROI upper-left coordinate to dataset pixel coordinates.
                    col_offset_float, row_offset_float = ~transform * (minx, maxy)
                    col_offset = math.floor(col_offset_float)
                    row_offset = math.floor(row_offset_float)

                    # Determine the indices in the output ROI array where the source data should be placed.
                    np_col_idx = abs(col_offset) if col_offset < 0 else 0
                    np_row_idx = abs(row_offset) if row_offset < 0 else 0

                    # Adjust the window size if the ROI exceeds dataset boundaries.
                    if (col_offset + width) > img_width:
                        window_width = img_width - col_offset
                    else:
                        window_width = width

                    if (row_offset + height) > img_height:
                        window_height = img_height - row_offset
                    else:
                        window_height = height

                    window = Window(col_offset, row_offset, window_width, window_height)

                    # Read the first band from the dataset within the computed window.
                    data = dataset.read(window=window)

                    if band == "Fmask":
                        roi_array = np.full((height, width), 255, dtype=np.uint8)
                    else:
                        roi_array = np.full((height, width), -9999, dtype=np.int16)

                    # Place the read data into the ROI array at the correct position.
                    roi_array[
                        np_row_idx : np_row_idx + window_height,
                        np_col_idx : np_col_idx + window_width,
                    ] = data[0]

                    date = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%fZ")

                    # Compute the x and y coordinates for the pixel centers
                    tgt_x, tgt_y = _get_roi_xr_utm_cordts(
                        roi, img_crs, pixel_width, pixel_height
                    )

                    # Create an xarray DataArray with dimensions ("time", "y", "x").
                    roi_da = xr.DataArray(
                        data=roi_array[None, :, :],
                        coords={
                            "time": [date],
                            "y": tgt_y,
                            "x": tgt_x,
                        },
                        dims=("time", "y", "x"),
                        name=band,
                        attrs={"crs": img_crs, "sat_id": sat_id, "tile_id": tile_id},
                    )

                    # Reprojecting the ROI array to the ROI CRS if necessary.
                    roi_crs = _get_bbox_utm_code(roi)
                    if img_crs != roi_crs:
                        roi_da = _reproject_xr_da(
                            roi_da, roi, roi_crs, pixel_width, pixel_height
                        )
                        roi_da.attrs["crs"] = roi_crs
                        roi_da.attrs["sat_id"] = sat_id
                        roi_da.attrs["tile_id"] = tile_id

                    return roi_da

        except requests.RequestException as e:
            if "401" in str(e) or "403" in str(e):
                print(f"Credential error. Check the validity of the token: {e}")
                print("Exiting...")
                # Early stopping for 401
                stop_event.set()
                break

            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                delay = min(delay * 2, max_delay)  # Exponential backoff
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # Wait before retrying
            else:
                print("Max retries reached. Request failed.")
                return None

        except Exception as e:
            print(f"Error during processing: {e}")
            return None
