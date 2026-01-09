""" Test functions for era5.py """


import xarray as xr
import numpy as np

from era5vis import era5

def test_horiz_cross_section(retrieve_param_level_time_from_ds, datafile):
    '''
    Test extraction of a horizontal cross section at a given pressure level and time.
    '''
    # extract test parameters
    param, level, time = retrieve_param_level_time_from_ds

    # test using time index
    da = era5.horiz_cross_section(param=param, lvl=level, time=0, datafile=datafile)
    assert isinstance(da, xr.DataArray)
    assert set(da.dims) == {'latitude', 'longitude'}
    assert da.pressure_level.item() == level
    # compare datetime with explicit nanosecond unit
    assert np.datetime64(da.valid_time.item(), 'ns') == time

    # test using valid_time
    # convert np.datetime64 to string for horiz_cross_section (it expects str)
    time_str = np.datetime_as_string(time, unit='m')  # e.g., '2025-10-01T00:00'
    da2 = era5.horiz_cross_section(param=param, lvl=level, time=time_str, datafile=datafile)
    assert isinstance(da2, xr.DataArray)
    assert set(da2.dims) == {'latitude', 'longitude'}
    assert da2.pressure_level.item() == level
    assert np.datetime64(da2.valid_time.item(), 'ns') == time
