""" Test functions for era5.py """


import xarray as xr
import numpy as np
import pandas as pd

from era5vis import era5

def test_horiz_cross_section(retrieve_param_level_time_from_ds, datafile):
    """
    Test extraction of a horizontal cross section at a given pressure level and time.
    """
    param, level, time_str = retrieve_param_level_time_from_ds

    # test using time index
    da = era5.horiz_cross_section(param=param, lvl=level, time=0, datafile=datafile)
    assert isinstance(da, xr.DataArray)
    assert set(da.dims) == {'latitude', 'longitude'}
    assert da.pressure_level.item() == level

    # convert the string from fixture to np.datetime64 for comparison
    expected_time = np.datetime64(pd.to_datetime(time_str))
    assert np.datetime64(da.valid_time.item(), 'ns') == expected_time

    # test using explicit time string
    da_time = era5.horiz_cross_section(param=param, lvl=level, time=time_str, datafile=datafile)
    assert np.datetime64(da_time.valid_time.item(), 'ns') == expected_time
    assert np.datetime64(da_time.valid_time.item(), 'ns') == expected_time
