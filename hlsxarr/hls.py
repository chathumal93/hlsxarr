import os
from .roi import RoiPolygon
from typing import Optional
from .process.read import _read
from .process.merge import _merge
from .process.search import _search
from .types import CollectionType, BandsType
from .exceptions import ProcessError
import xarray as xr


class HLSProcessor:
    def __init__(
        self,
        roi: dict,
        edl_token: Optional[str] = None,
    ):
        self.roi = RoiPolygon(geometry=roi)
        self._edl_token = edl_token or os.getenv("EDL_TOKEN")

        if not self._edl_token:
            raise ValueError(
                "An Earthdata Login token is required to access HLS data. Set the EDL_TOKEN environment variable."
            )

    def process(
        self,
        start_date: str,
        end_date: str,
        collections: CollectionType,
        bands: BandsType,
        limit: int,
        workers: int,
    ) -> Optional[xr.Dataset]:
        """Process HLS data

        Args:
            start_date (str): Start date for the search
            end_date (str): End date for the search
            collections (CollectionType): HLS collections to search
            bands (BandsType): Bands to read
            limit (int): Maximum number of scenes to search
            workers (int): Number of parallel workers to use for reading data

        Returns:
            xr.Dataset: Merged xarray dataset
        """

        try:
            print("Searching HLS data...")
            df = _search(
                roi=self.roi,
                start_date=start_date,
                end_date=end_date,
                collections=collections,
                bands=bands,
                limit=limit,
            )

            if df.empty:
                print("No data found")
                return
            else:
                xr_da_list = _read(
                    roi=self.roi,
                    df=df,
                    workers=workers,
                    edl_token=self._edl_token,
                )
                if xr_da_list:
                    processes_xr_dataset = _merge(df=df, da_list=xr_da_list)

                    return processes_xr_dataset
                else:
                    print("Processing incomplete")
                    return
        except Exception as e:
            raise ProcessError(str(e))
