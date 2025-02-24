import os

# from pathlib import Path
from .roi import RoiPolygon
from typing import Optional, List
import logging
from .process.reads import _read
from .process.merge import _merge
from .process.search import _search
from .types import CollectionType, BandsType
import xarray as xr


class HLSProcessor:
    def __init__(
        self,
        roi: RoiPolygon,
        edl_token: Optional[str] = None,
    ):
        self.roi = roi
        self._edl_token = edl_token or os.getenv("EDL_TOKEN")

        if not isinstance(roi, RoiPolygon):
            raise ValueError("Invalid ROI type. Expected RoiPolygon")

        if not self._edl_token:
            raise ValueError(
                "An Earthdata Login token is required to access HLS data. Set the EDL_TOKEN environment variable."
            )
        # Set up logging
        logging.basicConfig(level=logging.INFO)

    def process(
        self,
        start_date: str,
        end_date: str,
        collections: CollectionType,
        bands: BandsType,
        limit: int,
        workers: int,
    ) -> Optional[List[xr.DataArray]]:
        """"""
        logging.info("Processing HLS data")

        try:
            df = _search(
                roi=self.roi,
                start_date=start_date,
                end_date=end_date,
                collections=collections,
                bands=bands,
                limit=limit,
            )

            if df.empty:
                logging.info("No data found")
                return
            else:
                logging.info(f"Found {len(df)} scenes")

                xr_da_list = _read(
                    roi=self.roi,
                    df=df,
                    workers=workers,
                    edl_token=self._edl_token,
                )
                if xr_da_list:
                    logging.info("Merging data")
                    processes_xr_dataset = _merge(df=df, da_list=xr_da_list)
                    logging.info("Processing complete")
                    return processes_xr_dataset
                else:
                    logging.info("Processing incomplete")
                    return
        except Exception as e:
            logging.error(f"Error in the processing: {e}")
            raise e
