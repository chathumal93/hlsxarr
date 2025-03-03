import pytest
from unittest.mock import patch
import numpy as np
import xarray as xr
from rasterio.transform import from_origin
from rasterio.crs import CRS
from hlsxarr.process.stac2xrda import _stac2xrda
import rasterio


@pytest.fixture
def roi():
    # ROI CRS (UTM Zone 17N, EPSG:32617)
    return {
        "coordinates": [
            [
                [-78.60065306329707, 36.723116361254284],
                [-78.60065306329707, 36.60070088520398],
                [-78.33799755283125, 36.60070088520398],
                [-78.33799755283125, 36.723116361254284],
                [-78.60065306329707, 36.723116361254284],
            ]
        ],
        "type": "Polygon",
    }


# Helper function to create an in-memory raster (mock raster)
def create_in_memory_raster(same_crs: bool):
    data = np.ones((3660, 3660), dtype=np.uint8)

    if same_crs:
        # Same CRS (UTM Zone 17N, EPSG:32617)
        transform = from_origin(699960.00, 4100040.00, 30, 30)
        crs = CRS.from_epsg(32617)
    else:
        # Different CRS (UTM Zone 18N, EPSG:32618)
        transform = from_origin(199980.00, 4100040.00, 30, 30)
        crs = CRS.from_epsg(32618)

    # Use MemoryFile to simulate writing to an in-memory file
    memfile = rasterio.io.MemoryFile()
    with memfile.open(
        driver="GTiff",
        count=1,
        dtype="uint8",
        width=3660,
        height=3660,
        crs=crs,
        transform=transform,
    ) as dataset:
        dataset.write(data, 1)

    return memfile


@pytest.fixture
def mock_memory_raster():
    return create_in_memory_raster()


# Mocking the requests.get and other required functions for the test
@patch("hlsxarr.process.stac2xrda.requests.get")
@patch("hlsxarr.process.stac2xrda.MemoryFile")
def test_stac2xrda_with_reproject(
    mock_memory_file,
    mock_get,
    roi,
):
    # Mock the requests.get response
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"test"

    # Mock MemoryFile to return our in-memory raster
    mock_memory_file.return_value = create_in_memory_raster(same_crs=False)

    da = _stac2xrda(
        roi=roi,
        token="test_token",
        url="https://test.url",
        dt="2025-01-02T16:13:06.729Z",
        sat_id="S30",
        tile_id="T18STF",
        band="RED",
    )

    mock_get.assert_called_once_with(
        "https://test.url", headers={"Authorization": "Bearer test_token"}, stream=True
    )
    assert isinstance(da, xr.DataArray), "Expected result to be an xarray DataArray"
    mock_memory_file.assert_called_once()
    assert da.attrs["crs"] == "EPSG:32617"


@patch("hlsxarr.process.stac2xrda.requests.get")
@patch("hlsxarr.process.stac2xrda.MemoryFile")
def test_stac2xrda_without_reproject(
    mock_memory_file,
    mock_get,
    roi,
):
    # Mock the requests.get response
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"test"

    # Mock MemoryFile to return our in-memory raster
    mock_memory_file.return_value = create_in_memory_raster(same_crs=True)

    da = _stac2xrda(
        roi=roi,
        token="test_token",
        url="https://test.url",
        dt="2025-01-02T16:13:06.729Z",
        sat_id="S30",
        tile_id="T18STF",
        band="RED",
    )

    mock_get.assert_called_once_with(
        "https://test.url", headers={"Authorization": "Bearer test_token"}, stream=True
    )
    assert isinstance(da, xr.DataArray), "Expected result to be an xarray DataArray"
    mock_memory_file.assert_called_once()
    assert da.attrs["crs"] == "EPSG:32617"
