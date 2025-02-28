from shapely.geometry import shape, Polygon
from pyproj import Transformer
from typing import List, Optional
import math
import numpy as np


def _get_bbox_utm_code(geometry: dict) -> str:
    """Get the UTM CRS code for the geometry"""
    coordinates = geometry["coordinates"][0]

    # Get the central longitude and latitude
    lons = [coord[0] for coord in coordinates]
    lats = [coord[1] for coord in coordinates]
    central_lon = (min(lons) + max(lons)) / 2
    central_lat = (min(lats) + max(lats)) / 2

    # Get the UTM zone and CRS
    utm_zone = int((central_lon + 180) // 6) + 1
    utm_crs = f"EPSG:326{utm_zone}" if central_lat >= 0 else f"EPSG:327{utm_zone}"

    return utm_crs


def _get_projected_bounds(geometry, image_crs) -> Optional[List[float]]:
    """Projecting WGS84 ROI to image UTM projection"""
    geometry = shape(geometry)

    # Initialize the transformer for CRS transformation
    transformer = Transformer.from_crs("EPSG:4326", image_crs, always_xy=True)

    if isinstance(geometry, Polygon):
        # Transform the exterior coordinates
        exterior_coords = [
            transformer.transform(x, y) for x, y in geometry.exterior.coords
        ]
        # Create a new Polygon with transformed coordinates (no interior handling)
        transformed_geometry = Polygon(exterior_coords)
        # Calculate the bounding box (minx, miny, maxx, maxy)
        minx, miny, maxx, maxy = transformed_geometry.bounds
        return minx, miny, maxx, maxy

    return None


def _get_roi_xr_utm_cordts(roi: dict, crs: str, pixel_w: int, pixel_h: int) -> tuple:
    """Get the x and y coordinates of the ROI in UTM projection for xr dataarray"""
    # Get the bounds of the ROI in UTM coordinates
    minx, miny, maxx, maxy = _get_projected_bounds(roi, crs)
    # Get the width and height of the ROI in pixels
    width = math.floor((maxx - minx) / pixel_w)
    height = math.floor((maxy - miny) / pixel_h)

    # Get corresponding x and y coordinates for the pixel centers for xr dataarray
    x_coords = minx + pixel_w * (np.arange(width) + 0.5)
    y_coords = maxy - pixel_h * (np.arange(height) + 0.5)

    return x_coords, y_coords
