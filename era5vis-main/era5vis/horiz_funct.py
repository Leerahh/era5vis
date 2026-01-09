import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from era5vis import cfg
import scipy

def vert_cross_section(param, start, end, time, npoints=200):
    """Extract a vertical cross section from the ERA5 data.

    Parameters
    ----------
    param : str
        ERA5 variable (e.g. 'z', 'u', 'v')
    start : tuple(float, float)
        (lat_start, lon_start)
    end : tuple(float, float)
        (lat_end, lon_end)
    time : str or int
        time string (label) or time index (integer), like horiz_cross_section
    npoints : int
        number of samples along the cross-section line

    Returns
    -------
    da : xarray.DataArray
        2D DataArray of param with dims (pressure_level, point).
        Includes coordinates:
          - valid_time (scalar)
          - pressure_level (1D)
          - lat(point), lon(point)
    """

    lat0, lon0 = start
    lat1, lon1 = end

    # Create sampling points along a straight line in (lat, lon)
    lats = np.linspace(lat0, lat1, npoints)
    lons = np.linspace(lon0, lon1, npoints)

    # Use a "point" dimension so interp returns (pressure_level, point)
    pts = xr.DataArray(np.arange(npoints), dims=("point",), name="point")
    lat_pts = xr.DataArray(lats, dims=("point",), coords={"point": pts})
    lon_pts = xr.DataArray(lons, dims=("point",), coords={"point": pts})

    # Same time-selection logic as horiz_cross_section
    with xr.open_dataset(cfg.datafile).load() as ds:
        if isinstance(time, str):
            da_t = ds[param].sel(valid_time=time)
        elif isinstance(time, int):
            da_t = ds[param].isel(valid_time=time)
        else:
            raise TypeError("time must be a time format string or integer")

        # Interpolate onto the transect (keeps all pressure levels)
        da = da_t.interp(latitude=lat_pts, longitude=lon_pts)

    # Add convenient point coordinates for plotting/inspection
    da = da.assign_coords(lat=("point", lats), lon=("point", lons))

    # Ensure expected dim order (vertical first)
    da = da.transpose("pressure_level", "point")

    return da




