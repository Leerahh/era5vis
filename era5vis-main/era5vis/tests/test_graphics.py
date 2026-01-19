"""
Test functions for graphics.py

Updated by Lina Brückner, January 2026:
    - Testing plot_scalar_with_wind
    - Testing extract_skewT_profile
    - Testing plot_skewT using extracted profiles
"""

import matplotlib.pyplot as plt
import xarray as xr

from era5vis import graphics, cfg


def test_plot_scalar_with_wind_labels(retrieve_param_level_from_ds):
    """Test scalar_wind plotting returns figure with correct labels."""

    param, level = retrieve_param_level_from_ds
    u, v = "u", "v"

    with xr.open_dataset(cfg.scalar_wind_datafile) as ds:
        da = ds[param].sel(pressure_level=level).isel(valid_time=0)
        u_da = ds[u].sel(pressure_level=level).isel(valid_time=0)
        v_da = ds[v].sel(pressure_level=level).isel(valid_time=0)

    fig = graphics.plot_scalar_with_wind(da, u_da, v_da)

    texts = [t.get_text() for t in fig.findobj(plt.Text)]
    assert any("Longitude" in txt for txt in texts)
    assert any("Latitude" in txt for txt in texts)
    assert any(da.long_name in txt for txt in texts)

    plt.close(fig)


def test_plot_scalar_with_wind_saving(tmp_path, retrieve_param_level_from_ds):
    """Test saving scalar_wind plot to PNG."""

    param, level = retrieve_param_level_from_ds
    u, v = "u", "v"

    with xr.open_dataset(cfg.scalar_wind_datafile) as ds:
        da = ds[param].sel(pressure_level=level).isel(valid_time=0)
        u_da = ds[u].sel(pressure_level=level).isel(valid_time=0)
        v_da = ds[v].sel(pressure_level=level).isel(valid_time=0)

    fpath = tmp_path / "scalar_wind_test.png"

    fig = graphics.plot_scalar_with_wind(da, u_da, v_da, savepath=fpath)

    assert fig is not None
    assert fpath.exists()
    assert fpath.suffix == ".png"

    plt.close(fig)


def test_extract_and_plot_skewT(tmp_path):
    """
    Test Skew-T profile extraction AND plotting.
    """

    # get a valid lat/lon/time from example dataset
    with xr.open_dataset(cfg.skewT_datafile) as ds:
        lat = float(ds.latitude.values[0])
        lon = float(ds.longitude.values[0])
        time = str(ds.valid_time.values[0])

    # --- extraction ---
    p, T, Td, u, v = graphics.extract_skewT_profile(
        lat=lat,
        lon=lon,
        time=time,
        datafile=str(cfg.skewT_datafile),
    )

    # basic sanity checks on extracted profiles
    assert p.size > 0
    assert T.size == p.size
    assert Td.size == p.size
    assert u.size == p.size
    assert v.size == p.size

    # --- plotting ---
    fpath = tmp_path / "skewT_test.png"

    fig = graphics.plot_skewT(
        p=p,
        T=T,
        Td=Td,
        u=u,
        v=v,
        lat=lat,
        lon=lon,
        time=time,
        savepath=fpath,
    )

    assert fig is not None
    assert fpath.exists()
    assert fpath.suffix == ".png"

    plt.close(fig)path.suffix == '.png'

    plt.close(fig)
