from .types import Collections, Bands


class AreaTooLargeError(Exception):
    def __init__(self, area: float, limit: float):
        super().__init__(
            f"AreaTooLargeError: Area of {area:.2f} km² exceeds maximum area of {limit} km²"
        )


class InvalidCollectionError(Exception):
    def __init__(self, collection):
        super().__init__(
            f"InvalidCollectionError: Invalid collection: {collection}, Valid collections are: {Collections.COLLECTIONS}"
        )


class InvalidBandError(Exception):
    def __init__(self, band):
        super().__init__(
            f"InvalidBandError: Invalid band: {band}, valid bands are: {Bands.BANDS}"
        )


class ProcessError(Exception):
    def __init__(self, message):
        super().__init__(f"ProcessError: {message}")


class DataReadError(Exception):
    def __init__(self, message):
        super().__init__(f"DataReadError: {message}")
