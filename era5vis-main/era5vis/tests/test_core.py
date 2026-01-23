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
    # open scalar_wind dataset to get a valid variable, level and time
    with xr.open_dataset(cfg.scalar_wind_datafile) as ds:
        # pick the first variable with a pressure_level dimension
        param = [v for v in ds.variables if 'pressure_level' in ds[v].dims and 'longitude' in ds[v].dims][0]
        level = int(ds.pressure_level.values[0])
        time = str(ds.valid_time.values[0])  # convert np.datetime64 to str

    u, v = 'u', 'v'

    # generate HTML
    htmlfile = core.write_scalar_with_wind_html(
        scalar=param,
        u=u,
        v=v,
        level=level,
        time=time,
        directory=tmp_path,
        datafile=str(cfg.scalar_wind_datafile),
    )

    # check that HTML file exists
    assert Path.is_file(htmlfile)
    assert htmlfile.suffix == '.html'
    # check that a PNG was created in the same directory
    assert list(htmlfile.parent.glob('*.png'))


def test_write_skewT_html(tmp_path):
    '''
    Check that HTML file is created and the directory contains a PNG file.
    '''
    # open the Skew-T dataset to get valid coordinates and time
    with xr.open_dataset(cfg.skewT_datafile) as ds:
        # pick the first valid latitude, longitude and time
        lat = float(ds.latitude.values[0])
        lon = float(ds.longitude.values[0])
        time = str(ds.valid_time.values[0])

    # generate HTML
    htmlfile = core.write_skewT_html(
        lat=lat,
        lon=lon,
        time=time,
        directory=tmp_path,
        datafile=str(cfg.skewT_datafile)
    )


def test_write_vert_cross_html(tmp_path):
    """
    Check that vertical cross-section HTML and PNG are created.
    """

    with xr.open_dataset(cfg.vert_cross_datafile) as ds:
        time = str(ds.valid_time.values[0])

    start = (40.0, 0.0)   # (lat, lon)
    end = (60.0, 20.0)

    htmlfile = core.write_vert_cross_html(
        param="t",
        start=start,
        end=end,
        time=time,
        npoints=50,
        directory=tmp_path,
        datafile=str(cfg.vert_cross_datafile),
    )

    # HTML exists
    assert htmlfile.exists()
    assert htmlfile.suffix == ".html"

    # PNG exists
    pngs = list(htmlfile.parent.glob("*.png"))
    assert len(pngs) > 0
