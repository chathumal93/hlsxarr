import pandas as pd
from ..roi import RoiPolygon
from ..types import BandsType, CollectionType, Collections, Bands
from typing import List
from ..exceptions import InvalidCollectionError, InvalidBandError
from pystac_client import Client


def _search(
    roi: RoiPolygon,
    start_date: str,
    end_date: str,
    collections: CollectionType,
    bands: BandsType,
    limit: int,
) -> pd.DataFrame:
    """Search for HLS data using the STAC API.
    Args:
        roi (RoiPolygon): The region of interest.
        start_date (str): The start date.
        end_date (str): The end date.
        collections (CollectionType): The collection type.
        bands (BandsType): The bands type.
        limit (int): The limit.
    Returns:
        pd.DataFrame: A pandas DataFrame.
    """

    HLS_STAC_URL = "https://cmr.earthdata.nasa.gov/stac/LPCLOUD"

    if not isinstance(collections, list):
        raise ValueError("collections should be a list")

    for collection in collections:
        if collection not in Collections.COLLECTIONS:
            raise InvalidCollectionError(collection)

    if not isinstance(bands, list):
        raise ValueError("Bands should be a list")

    for band in bands:
        if band not in Bands.BANDS:
            raise InvalidBandError(band)

    catalog = Client.open(HLS_STAC_URL)
    search = catalog.search(
        collections=collections,
        intersects=roi.geometry,
        datetime=f"{start_date}/{end_date}",
        limit=limit,
    )
    items = list(search.item_collection())
    df = _create_dataframe(items, bands)

    return df


def _create_dataframe(items: List, bands: BandsType) -> pd.DataFrame:
    """Create a pandas DataFrame from a list of STAC items.
    Args:
        items (List): A list of STAC items.
        bands (BandsType): bands.
    Returns:
        pd.DataFrame: A pandas DataFrame.
    """

    rows = []
    for item in items:
        date = item.properties["datetime"]
        satdata_id_parts = item.id.split(".")
        sat_id = satdata_id_parts[1]
        tile_id = satdata_id_parts[2]
        base_path = f"{satdata_id_parts[0]}{satdata_id_parts[1]}.020"
        for band in bands:
            if sat_id == "L30":
                stac_band_id = Bands.L30_BANDS[band]
            elif sat_id == "S30":
                stac_band_id = Bands.S30_BANDS[band]
            stac_url = (
                f"https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/"
                f"{base_path}/{item.id}/{item.id}.{stac_band_id}.tif"
            )
            rows.append(
                {
                    "sat_id": sat_id,
                    "tile_id": tile_id,
                    "date": date,
                    "stac_url": stac_url,
                    "band": band,
                }
            )

    df = pd.DataFrame(rows)
    return df
