
``` python
xr_ds = hls.process(
    roi=roi_dict,
    start_date="2025-01-01",
    end_date="2025-01-07",
    collections=["HLSS30.v2.0", "HLSL30.v2.0"],
    bands=["CA", "BLUE", "GREEN", "RED", "NIR", "SWIR1", "SWIR2", "FMASK"],
    limit=100,
    workers=8,
    max_area_km2=1000,
)
```
```
Searching HLS data...
Found 48 urls
Reading HLS Data: 100%|███████████████████████| 48/48 [00:29<00:00,  1.62file/s]
```



```
<xarray.Dataset> Size: 34MB
Dimensions:  (time: 6, y: 473, x: 794)
Coordinates:
  * time     (time) datetime64[ns] 48B 2025-01-02T16:13:06.729000 ... 2025-01...
  * x        (x) float64 6kB 7.143e+05 7.143e+05 ... 7.38e+05 7.381e+05
  * y        (y) float64 4kB 4.067e+06 4.067e+06 ... 4.053e+06 4.053e+06
Data variables:
    BLUE     (time, x, y) int16 5MB -9999 -9999 -9999 -9999 ... 97 112 118 137
    CA       (time, x, y) int16 5MB -9999 -9999 -9999 -9999 ... 73 73 75 97
    FMASK    (time, x, y) uint8 2MB 241 241 241 241 241 241 ... 64 64 64 64 64
    GREEN    (time, x, y) int16 5MB -9999 -9999 -9999 -9999 ... 209 217 236 278
    NIR      (time, x, y) int16 5MB -9999 -9999 -9999 -9999 ... 1820 2014 2173
    RED      (time, x, y) int16 5MB -9999 -9999 -9999 -9999 ... 153 160 170 231
    SAT_ID   (time) uint8 6B 1 1 1 1 0 0
    SWIR1    (time, x, y) int16 5MB -9999 -9999 -9999 -9999 ... 628 714 919 1035
    SWIR2    (time, x, y) int16 5MB -9999 -9999 -9999 -9999 ... 271 298 386 473
Attributes:
    crs:      EPSG:32617
    sat_ids:  L30 : 0, S30 : 1
```