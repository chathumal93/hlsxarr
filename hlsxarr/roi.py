from .utils import _get_projected_bounds, _get_bbox_utm_code
from .exceptions import AreaTooLargeError


class RoiPolygon:
    def __init__(self, geometry: dict, max_area_km2: float):
        self.geometry = geometry
        self._crs = _get_bbox_utm_code(self.geometry)
        self._area = self._calculate_area()
        self._max_area_km2 = max_area_km2

        # Validate the ROI area
        self._validate_roi()

    def _validate_roi(self):
        """Helper function to validate the ROI type and area."""
        if self.geometry["type"] != "Polygon":
            raise ValueError(
                "Invalid ROI type. Only Geojson Polygon Geometry is supported."
            )

        if self._area > self._max_area_km2:
            raise AreaTooLargeError(self._area, self._max_area_km2)

    def _calculate_area(self) -> float:
        """Helper function to calculate the area of the ROI."""
        minx, miny, maxx, maxy = _get_projected_bounds(self.geometry, self._crs)
        return round((maxx - minx) * (maxy - miny) / 1e6, 2)

    @property
    def area(self) -> float:
        return self._area

    @property
    def crs(self) -> int:
        return self._crs
