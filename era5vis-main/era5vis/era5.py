"""Functions interacting with the ERA5 dataset. """

import xarray as xr
import numpy as np
import pandas as pd


def check_file_availability(datafile):
    """Check if the ERA5 data file is available."""
    try:
        with xr.open_dataset(datafile).load() as ds:
            pass
    except FileNotFoundError:
        raise FileNotFoundError(
            f"The specified data file does not exist. Please set a valid path in cfg.py."
        )
    except Exception as e:
        raise RuntimeError(
            f"Error loading data file '{datafile}': {e}"
        )


def check_data_availability(param, level=None, time=None, time_ind=None, datafile=None):
     with xr.open_dataset(datafile).load() as ds:
        
        # --- check variable ---
        if param not in ds.variables:
            raise KeyError(
                f"Variable '{param}' not found in data file. "
                f"Available variables: {list(ds.variables)}"
            )

        da = ds[param]

        # --- check model level ---
        if level is not None:
            if "pressure_level" not in da.dims:
                raise KeyError(
                    f"Variable '{param}' has no pressure_level dimension."
                )

            if level not in da["pressure_level"].values:
                raise ValueError(
                    f"Pressure level {level} not available for variable '{param}'. "
                    f"Available levels: {da['pressure_level'].values}"
                )

            # --- check time by value ---
        if time is not None:
            if "valid_time" not in da.dims:
                raise KeyError(
                    f"Variable '{param}' has no valid_time dimension."
                )

            # normalize user input → numpy.datetime64
            try:
                time_dt = np.datetime64(pd.to_datetime(time))
            except Exception:
                raise ValueError(
                    f"Time '{time}' could not be parsed as a datetime."
                )

            times = da["valid_time"].values

            if time_dt not in times:
                raise ValueError(
                    f"Time {time_dt} not available for variable '{param}'. "
                    f"Available time range: {times.min()} – {times.max()}"
                )

            
        # --- check time by index ---
        if time_ind is not None:
            if "valid_time" not in da.dims:
                raise KeyError(
                    f"Variable '{param}' has no valid_time dimension."
                )

            if not (0 <= time_ind < da.sizes["valid_time"]):
                raise IndexError(
                    f"time_ind={time_ind} out of bounds for variable '{param}'. "
                    f"Valid range: 0 … {da.sizes['valid_time'] - 1}"
                )

            
def horiz_cross_section(param, lvl, time, datafile):
    """Extract a horizontal cross section from the ERA5 data.
    
    Parameters
    ----------
    param: str
        ERA5 variable
    lvl : integer
        model pressure level (hPa)
    time : str or integer
        time string or time index

    Returns
    -------
    da: xarray.DataArray
        2D DataArray of param
    """

    # use either sel or sel depending on the type of time (index or date format)
    with xr.open_dataset(datafile).load() as ds:
        if isinstance(time, str):
            da = ds[param].sel(pressure_level=lvl).sel(valid_time=time, method="nearest")
        elif isinstance(time, int):
            da = ds[param].sel(pressure_level=lvl).isel(valid_time=time)
        else:
            raise TypeError('time must be a time format string or integer')

    return da
