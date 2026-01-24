"""
ERA5 data access and validation utilities.

This module contains helper functions for interacting with ERA5 NetCDF
datasets. It provides functionality to:

- verify that an ERA5 data file exists and can be opened
- validate the availability of variables, pressure levels and times
- extract horizontal cross sections at a given pressure level and time

Edits:
 Leah Herrfurth, December 2025
    - Added check_file_availability
    
"""

import xarray as xr
import numpy as np
import pandas as pd


def check_file_availability(datafile):
    """
    Check whether an ERA5 NetCDF data file exists and can be opened.

    This function attempts to open and fully load the dataset using
    xarray. It is intended as an early sanity check before performing
    any data extraction or plotting.

    Parameters
    ----------
    datafile : str or pathlib.Path
        Path to the ERA5 NetCDF file.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    RuntimeError
        If the file exists but cannot be opened or parsed.
    """

    # attempt to open and fully load the dataset
    try:
        with xr.open_dataset(datafile).load() as ds:
            pass
    except FileNotFoundError:
        raise FileNotFoundError(
            f"The specified data file does not exist.
             Please set a valid path in cfg.py."
        )
    except Exception as e:
        raise RuntimeError(
            f"Error loading data file '{datafile}': {e}"
        )


def check_data_availability(
 param,
 level=None,
 time=None,
 time_ind=None,
 datafile=None
):
    """
    Check whether a variable, pressure level, and time exist in an ERA5 dataset.

    This function performs a series of validation checks to ensure that
    requested data are available before attempting extraction or plotting.

    Parameters
    ----------
    param : str
        Name of the ERA5 variable to check.
    level : int, optional
        Pressure level in hPa to validate.
    time : str, optional
        Datetime string compatible with the ERA5 ``valid_time`` coordinate.
    time_ind : int, optional
        Time index to validate.
    datafile : str or pathlib.Path
        Path to the ERA5 NetCDF file.

    Raises
    ------
    KeyError
        If the variable or a required dimension is missing.
    ValueError
        If the requested pressure level or time value is not available.
    IndexError
        If the requested time index is out of bounds.
    """

    # open and fully load the dataset to ensure all metadata are available
    with xr.open_dataset(datafile).load() as ds:
        # check variable existence
        if param not in ds.variables:
            raise KeyError(
                f"Variable '{param}' not found in data file. "
                f"Available variables: {list(ds.variables)}"
            )

        da = ds[param]

        # pressure level check
        if level is not None:
            # ensure the variable has a pressure level dimension
            if "pressure_level" not in da.dims:
                raise KeyError(
                    f"Variable '{param}' has no pressure_level dimension."
                )

            # ensure the requested pressure level exists
            if level not in da["pressure_level"].values:
                raise ValueError(
                    f"Pressure level {level} not available for variable '{param}'. "
                    f"Available levels: {da['pressure_level'].values}"
                )

        # time check
        if time is not None:
            # ensure the variable has a time dimension
            if "valid_time" not in da.dims:
                raise KeyError(
                    f"Variable '{param}' has no valid_time dimension."
                )

            # convert user input to numpy.datetime64
            try:
                time_dt = np.datetime64(pd.to_datetime(time))
            except Exception:
                raise ValueError(
                    f"Time '{time}' could not be parsed as a datetime.
                     Time must follow the format 'YYYYmmddHHMM'."
                )

            times = da["valid_time"].values

            # ensure the requested time exists in the dataset
            if time_dt not in times:
                raise ValueError(
                    f"Time {time_dt} not available for variable '{param}'. "
                    f"Available time range: {times.min()} – {times.max()}"
                )

        # check time by index
        if time_ind is not None:
            if "valid_time" not in da.dims:
                raise KeyError(
                    f"Variable '{param}' has no valid_time dimension."
                )

            if not (0 <= time_ind < da.sizes["valid_time"]):
                raise IndexError(
                    f"time_ind={time_ind} out of bounds for variable '{param}'."
                    f"Valid range: 0 … {da.sizes['valid_time'] - 1}"
                )

            
def horiz_cross_section(param, lvl, time, datafile):
    """
    Extract a horizontal cross section from ERA5 data.

    The cross section is extracted at a given pressure level and time.
    Time can be specified either as a datetime string or as an integer
    index into the ``valid_time`` dimension.

    Parameters
    ----------
    param : str
        ERA5 variable name.
    lvl : int
        Pressure level in hPa.
    time : str or int
        Datetime string (e.g. ``YYYYmmddHHMM``) or time index.
    datafile : str or pathlib.Path
        Path to the ERA5 NetCDF file.

    
    Returns
    -------
    xarray.DataArray
        Two-dimensional DataArray representing the horizontal field
        at the specified pressure level and time.

    Raises
    ------
    TypeError
        If ``time`` is neither a string nor an integer.
    """
    
    # open and fully load dataset
    with xr.open_dataset(datafile).load() as ds:
        # select by nearest valid_time if time is given as a string
        if isinstance(time, str):
            da = ds[param].sel(pressure_level=lvl).sel(valid_time=time, method="nearest")
        # select by index if time is given as an integer
        elif isinstance(time, int):
            da = ds[param].sel(pressure_level=lvl).isel(valid_time=time)
        else:
            raise TypeError("Time must be a time format string or integer")

    return da
