"""
Tests for era5.py.

These tests validate ERA5 data extraction utilities such as
horizontal cross sections.

Edited by Lina Brückner, January 2026:
    - Added test_check_file_availability_valid
    - Added test_check_data_availability_valid
    - Added test_check_data_availability_invalid_variable
"""

import pytest
import numpy as np
import pandas as pd
import xarray as xr

from era5vis import era5
    

def test_check_file_availability_valid(datafile):
    era5.check_file_availability(datafile)


def test_check_data_availability_valid(retrieve_param_level_time_from_ds, datafile):
    param, level, time = retrieve_param_level_time_from_ds
    era5.check_data_availability(
        param=param,
        level=level,
        time=time,
        datafile=datafile,
    )


def test_check_data_availability_invalid_variable(datafile):
    with pytest.raises(KeyError):
        era5.check_data_availability(
            param="this_variable_does_not_exist",
            datafile=datafile,
        )


def test_horiz_cross_section(retrieve_param_level_time_from_ds, datafile):
    """
    Test horizontal cross section extraction at given pressure level and time.
    """
    param, level, time_str = retrieve_param_level_time_from_ds

    # test using time index
    da = era5.horiz_cross_section(
        param=param, lvl=level, time=0, datafile=datafile
    )
    assert isinstance(da, xr.DataArray)
    assert set(da.dims) == {"latitude", "longitude"}
    assert da.pressure_level.item() == level

    # convert the string from fixture to np.datetime64 for comparison
    expected_time = np.datetime64(pd.to_datetime(time_str))
    assert np.datetime64(da.valid_time.item(), "ns") == expected_time

    # test using explicit time string
    da_time = era5.horiz_cross_section(
        param=param, lvl=level, time=time_str, datafile=datafile
    )
    assert np.datetime64(da_time.valid_time.item(), "ns") == expected_time
