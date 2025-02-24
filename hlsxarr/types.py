from typing import List, Literal

# Type Definitions
BandsType = List[
    Literal[
        "CA",
        "BLUE",
        "GREEN",
        "RED",
        "NIR",
        "SWIR1",
        "SWIR2",
        "FMASK",
    ]
]

CollectionType = List[Literal["HLSL30.v2.0", "HLSS30.v2.0"]]


class Bands:
    BANDS = {
        "CA",
        "BLUE",
        "GREEN",
        "RED",
        "NIR",
        "SWIR1",
        "SWIR2",
        "FMASK",
    }

    L30_BANDS = {
        "CA": "B01",
        "BLUE": "B02",
        "GREEN": "B03",
        "RED": "B04",
        "NIR": "B05",
        "SWIR1": "B06",
        "SWIR2": "B07",
        "FMASK": "Fmask",
    }

    S30_BANDS = {
        "CA": "B01",
        "BLUE": "B02",
        "GREEN": "B03",
        "RED": "B04",
        "NIR": "B8A",
        "SWIR1": "B11",
        "SWIR2": "B12",
        "FMASK": "Fmask",
    }

    @staticmethod
    def is_valid_band(band: str) -> bool:
        """Check if a band is valid."""
        return band in Bands.BANDS


class Collections:
    COLLECTIONS = {
        "HLSL30.v2.0",
        "HLSS30.v2.0",
    }

    @staticmethod
    def is_valid_collection(collection: str) -> bool:
        """Check if a collection is valid."""
        return collection in Collections.COLLECTIONS
