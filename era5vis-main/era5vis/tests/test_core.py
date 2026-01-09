"""
    Test functions for core.py
    Updated by Lina Brückner, January 2026:
        - def test_write_scalar_with_wind_html(tmp_path)
        - def test_write_skewT_html(tmp_path)
"""


import xarray as xr

from pathlib import Path
from era5vis import core, cfg


def test_mkdir(tmpdir):

    # check that directory is indeed created as a directory
    directory = str(tmpdir.join('html_dir'))
    core.mkdir(directory)
    assert Path.is_dir(Path(directory))


def test_write_scalar_with_wind_html(tmp_path):
    '''
    Check that HTML file is created and the directory contains a PNG file.
    '''
    # open the scalar_wind dataset to get a valid variable, level, and time
    with xr.open_dataset(cfg.scalar_wind_datafile) as ds:
        # pick the first variable with a pressure_level dimension
        param = [v for v in ds.variables if 'pressure_level' in ds[v].dims and 'longitude' in ds[v].dims][0]
        level = int(ds.pressure_level.values[0])
        time = str(ds.valid_time.values[0])  # convert np.datetime64 → str

    u, v = 'u', 'v'

    # generate HTML
    htmlfile = core.write_scalar_with_wind_html(
        scalar=param,
        u=u,
        v=v,
        level=level,
        time=time,  # pass string instead of np.datetime64
        directory=tmp_path,
        datafile=str(cfg.scalar_wind_datafile),
    )

    # check the HTML file exists
    assert Path.is_file(htmlfile)
    assert htmlfile.suffix == '.html'
    # check that a PNG was created in the same directory
    assert list(htmlfile.parent.glob('*.png'))


def test_write_skewT_html(tmp_path):
    '''Check that HTML file is created and the directory contains a PNG file.'''
    # open the Skew-T dataset to get valid coordinates and time
    with xr.open_dataset(cfg.skewT_datafile) as ds:
        # pick the first valid latitude, longitude, and time
        lat = float(ds.latitude.values[0])
        lon = float(ds.longitude.values[0])
        time = str(ds.valid_time.values[0])  # convert to string

    # generate HTML
    htmlfile = core.write_skewT_html(
        lat=lat,
        lon=lon,
        time=time,
        directory=tmp_path,
        datafile=str(cfg.skewT_datafile)
    )
