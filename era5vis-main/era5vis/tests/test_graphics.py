"""
Test functions for graphics.py
Updated by Lina Brückner, January 2026:
    - def test_plot_scalar_with_wind_labels(retrieve_param_level_from_ds)
    - def test_plot_scalar_with_wind_saving(tmp_path, retrieve_param_level_from_ds)
    - def test_plot_skewT_saving(tmp_path)
"""


import matplotlib.pyplot as plt
import xarray as xr

from era5vis import graphics, cfg


def test_plot_scalar_with_wind_labels(retrieve_param_level_from_ds):
    '''Test scalar_wind plotting returns figure with correct labels.'''

    param, level = retrieve_param_level_from_ds
    u, v = 'u', 'v'

    # open dataset and extract a single time slice at the requested level
    with xr.open_dataset(cfg.scalar_wind_datafile) as ds:
        da = ds[param].sel(pressure_level=level).isel(valid_time=0)
        u_da = ds[u].sel(pressure_level=level).isel(valid_time=0)
        v_da = ds[v].sel(pressure_level=level).isel(valid_time=0)

    # generate figure
    fig = graphics.plot_scalar_with_wind(da, u_da, v_da)

    # collect all text elements in the figure
    texts = [t.get_text() for t in fig.findobj(plt.Text)]
    # check that axis labels appear in figure text
    assert any('Longitude' in txt for txt in texts)
    assert any('Latitude' in txt for txt in texts)
    assert any(da.long_name in txt for txt in texts)

    plt.close(fig)


def test_plot_scalar_with_wind_saving(tmp_path, retrieve_param_level_from_ds):
    '''Test saving scalar_wind plot to PNG.'''

    param, level = retrieve_param_level_from_ds
    u, v = 'u', 'v'

    # open dataset and extract a single time slice at the requested level
    with xr.open_dataset(cfg.scalar_wind_datafile) as ds:
        da = ds[param].sel(pressure_level=level).isel(valid_time=0)
        u_da = ds[u].sel(pressure_level=level).isel(valid_time=0)
        v_da = ds[v].sel(pressure_level=level).isel(valid_time=0)

    # define output path in temporary directory
    fpath = tmp_path / 'scalar_wind_test.png'

    # generate and save figure
    fig = graphics.plot_scalar_with_wind(da, u_da, v_da, savepath=fpath)

    # validate output
    assert fig is not None
    assert fpath.exists()
    assert fpath.suffix == '.png'

    plt.close(fig)


def test_plot_skewT_saving(tmp_path):
    '''Test Skew-T plotting saves a PNG.'''

    # open skewT dataset to get a valid lat/lon/time combination
    with xr.open_dataset(cfg.skewT_datafile) as ds:
        lat = float(ds.latitude.values[0])
        lon = float(ds.longitude.values[0])
        time = str(ds.valid_time.values[0])

    # define output path in temporary directory
    fpath = tmp_path / 'skewT_test.png'

    # generate and save figure
    fig = graphics.plot_skewT(
        lat=lat,
        lon=lon,
        time=time,
        datafile=str(cfg.skewT_datafile),
        savepath=fpath
    )

    # validate output
    assert fig is not None
    assert fpath.exists()
    assert fpath.suffix == '.png'

    plt.close(fig)
