import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_origin, Affine
from rasterio.warp import calculate_default_transform, reproject, Resampling
from ..utils import _get_roi_xr_utm_cordts
import warnings


def _reproject_xr_da(
    src_xr_arr: xr.DataArray,
    roi: dict,
    tgt_crs: str,
    pixel_width: int,
    pixel_height: int,
) -> xr.DataArray:
    """Reproject an xarray DataArray to a new coordinate reference system (CRS).

    Args:
        src_xr_arr (xr.DataArray): The source xarray DataArray.
        roi (dict): The region of interest.
        tgt_crs (str): The target CRS.
        pixel_width (int): The pixel width.
        pixel_height (int): The pixel height.

    Returns:
        xr.DataArray: The reprojected xarray DataArray.
    """
    # remove the NotGeoreferencedWarning
    warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

    src_width = src_xr_arr.sizes.get(key="x")
    src_height = src_xr_arr.sizes.get(key="y")
    src_left = src_xr_arr.coords["x"].min().item() - (pixel_width / 2)
    src_bottom = src_xr_arr.coords["y"].min().item() - (pixel_height / 2)
    src_right = src_xr_arr.coords["x"].max().item() + (pixel_width / 2)
    src_top = src_xr_arr.coords["y"].max().item() + (pixel_height / 2)
    src_transform = from_origin(src_left, src_top, pixel_width, pixel_height)

    tgt_transform, tgt_width, tgt_height = calculate_default_transform(
        src_crs=src_xr_arr.attrs["crs"],
        dst_crs=tgt_crs,
        width=src_width,
        height=src_height,
        left=src_left,
        top=src_top,
        right=src_right,
        bottom=src_bottom,
        resolution=(pixel_width, pixel_height),
    )

    tgt_transform = Affine(*tgt_transform)
    tgt_shape = (tgt_height, tgt_width)

    src_arr = src_xr_arr.values
    band = src_xr_arr.name

    tgt_arr = np.full(tgt_shape, np.nan, dtype=np.float32)
    if band == "Fmask":
        tgt_arr = np.full(tgt_shape, 255, dtype=np.uint8)
        no_data = 255
        data_type = np.uint8
    else:
        tgt_arr = np.full(tgt_shape, -9999, dtype=np.int16)
        no_data = -9999
        data_type = np.int16

    projected_data, projected_tansform = reproject(
        src_arr,
        tgt_arr,
        src_transform=src_transform,
        src_crs=src_xr_arr.attrs["crs"],
        dst_transform=tgt_transform,
        dst_crs=tgt_crs,
        resampling=Resampling.bilinear,
        dst_nodata=no_data,
        src_nodata=no_data,
    )

    pixel_width = abs(projected_tansform.a)
    pixel_height = abs(projected_tansform.e)

    # Compute the x and y coordinates for the pixel centers for projected dataarray
    x_coords = projected_tansform.c + pixel_width * (np.arange(tgt_width) + 0.5)
    y_coords = projected_tansform.f - pixel_height * (np.arange(tgt_height) + 0.5)

    # Create an xarray DataArray with dimensions ("time", "y", "x").
    projected_xr_da = xr.DataArray(
        name=band,
        data=projected_data[None, :, :],
        coords={
            "time": [src_xr_arr.time.values[0]],
            "y": y_coords,
            "x": x_coords,
        },
        dims=("time", "y", "x"),
        attrs={"crs": tgt_crs},
    )

    # Interpolation to the ROI based coordinates
    intp_tgt_x, intp_tgt_y = _get_roi_xr_utm_cordts(
        roi, tgt_crs, pixel_width, pixel_height
    )
    interpolated_da = projected_xr_da.interp(
        x=intp_tgt_x, y=intp_tgt_y, method="nearest"
    ).astype(data_type)

    return interpolated_da
