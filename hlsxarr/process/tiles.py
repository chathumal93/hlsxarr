import xarray as xr
import math


def _tile(dataset: xr.Dataset, tile_size: int, pad_value=int):
    print(f"cols: {dataset.sizes['x']}")
    print(f"rows: {dataset.sizes['y']}")
    tiles_x = math.ceil(dataset.sizes["x"] / tile_size)
    tiles_y = math.ceil(dataset.sizes["y"] / tile_size)
    for y in range(tiles_y):
        for x in range(tiles_x):
            print(f"Tile {y}, {x}")
            ds = dataset.isel(
                y=slice(y * tile_size, (y * tile_size) + tile_size),
                x=slice(x * tile_size, (x * tile_size) + tile_size),
            )
            # Check if the tile is smaller than the tile size and pad if necessary
            pad_x = tile_size - ds.sizes["x"] if ds.sizes["x"] < tile_size else 0
            pad_y = tile_size - ds.sizes["y"] if ds.sizes["y"] < tile_size else 0

            if pad_x > 0 or pad_y > 0:
                ds = ds.pad(
                    x=(0, pad_x),
                    y=(0, pad_y),
                    constant_values=pad_value,
                )
            print(ds)
