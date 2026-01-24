"""
Plotting utilities for ERA5 visualizations.

This module provides functions to visualize ERA5 pressure-level data,
including:

- Horizontal maps of scalar fields with overlaid wind vectors
- Vertical atmospheric soundings using Skew-T diagrams with hodographs
- Vertical cross sections

The functions in this module assume that ERA5 data follow standard
naming conventions (e.g. ``pressure_level``, ``valid_time``,
``latitude``, ``longitude``) and are provided either as
``xarray.DataArray`` objects or via ERA5 NetCDF files.

Updated by Lina Brückner, January 2026:
    - Added scalar-with-wind map plotting
    - Added Skew-T and hodograph plotting

Updated by Ilias, January 2026:
    - Added vertical cross section
"""

from datetime import datetime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import xarray as xr
from metpy.plots import SkewT, Hodograph
from metpy.units import units
import metpy.calc as mpcalc
import numpy as np
from metpy.calc import wind_speed


def plot_scalar_with_wind(da, u, v, savepath=None, step=9):
    """
    Plot a horizontal scalar field with wind vectors on a map.

    The scalar field is displayed using filled contours, while wind
    vectors are overlaid using quivers on a Plate Carrée projection.

    Parameters
    ----------
    da : xarray.DataArray
        Scalar field to plot (e.g. geopotential).
        Must contain ``latitude``, ``longitude``, ``pressure_level``,
        and ``valid_time`` coordinates.
    u : xarray.DataArray
        Zonal wind component corresponding to ``da``.
    v : xarray.DataArray
        Meridional wind component corresponding to ``da``.
    savepath : str or pathlib.Path, optional
        Path where the generated PNG image will be saved.
        If None, a filename is generated automatically.
    step : int, default 9
        Subsampling step for wind vectors. Values smaller than 1
        are internally reset to 1.

    Returns
    -------
    matplotlib.figure.Figure
        The generated Matplotlib figure.
    """

    # prevent step = 0
    if step < 1:
        step = 1

    # initiate figure
    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # extract time for title
    time = da.valid_time.to_numpy().astype('datetime64[ms]').astype(datetime)
    ax.set_title(
        f'{da.long_name} and wind barbs at {da.pressure_level.to_numpy()} '
        f'{da.pressure_level.units} ({time:%d %b %Y %H:%M})',
        fontsize=12
    )

    # plot scalar as filled contours
    cf = ax.contourf(da.longitude, da.latitude, da, levels=20, cmap='viridis')
    cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label(f'({da.units})')

    # subsample wind
    pu = u[::step, ::step]
    pv = v[::step, ::step]

    # plot wind quivers
    ax.quiver(
        pu.longitude,
        pu.latitude,
        pu,
        pv,
        pivot='middle',
        transform=ccrs.PlateCarree()
    )

    # add coastlines and borders
    ax.coastlines(color='green')
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    
    # add gridlines with labels
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.5,
        color='gray',
        alpha=0.7,
        linestyle='--'
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()

    # save figure
    if savepath is None:
        time_safe = str(time).replace(':', '-').replace(' ', '_')
        filename = f'scalar_wind_{da.name}_{da.pressure_level.to_numpy()}_{time_safe}.png'
        fig.savefig(filename, bbox_inches='tight')
        plt.close(fig)
    else:
        fig.savefig(savepath, bbox_inches='tight')
        plt.close(fig)

    return fig


def extract_skewT_profile(lat, lon, time, datafile, variables=None):
    """
    Extract a vertical thermodynamic and wind profile from ERA5 data.

    The profile is extracted at the nearest grid point to the specified
    latitude and longitude and at the specified time. Dewpoint temperature
    is computed from specific humidity using MetPy. Pressure levels
    are reordered from surface to upper atmosphere to comply with
    Skew-T plotting conventions.

    Parameters
    ----------
    lat : float
        Latitude in degrees.
    lon : float
        Longitude in degrees.
    time : str
        Datetime string compatible with the ERA5 ``valid_time`` coordinate.
    datafile : str or pathlib.Path
        Path to the ERA5 NetCDF data file.
    variables : dict, optional
        Mapping of logical variable names to dataset variable names.

    Returns
    -------
    p : pint.Quantity
        Pressure profile [hPa].
    T : pint.Quantity
        Temperature profile [°C].
    Td : pint.Quantity
        Dewpoint temperature profile [°C].
    u : pint.Quantity
        Zonal wind profile [m s⁻¹].
    """

    # use default ERA5 variable names 
    if variables is None:
        variables = {
            'T': 't',
            'q': 'q',
            'u': 'u',
            'v': 'v',
        }

    # open ERA5 netcdf dataset
    with xr.open_dataset(datafile) as ds:
        # extract temperature profile
        T_da = ds[variables['T']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest')

        # extract specific humidity profile
        q_da = ds[variables['q']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest')

        # extract zonal wind component profile
        u_da = ds[variables['u']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest') \

        # extract meridional wind component profile
        v_da = ds[variables['v']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest')

        # extract pressure levels
        p = T_da.pressure_level.values * units.hPa

        # convert units
        T = (T_da.values * units.kelvin).to(units.degC)
        u = u_da.values * units('m/s')
        v = v_da.values * units('m/s')
        # compute dewpoint from specific humidity and pressure
        Td = mpcalc.dewpoint_from_specific_humidity(p, q_da.values).to(units.degC)


        # order pressure profiles from the surface upwards
        p = p[::-1]
        T = T[::-1]
        Td = Td[::-1]
        u = u[::-1]
        v = v[::-1]

    return p, T, Td, u, v


def plot_skewT(p, T, Td, u, v, lat, lon, time, datafile=None, variables=None, savepath=None):
    """
    Plot a Skew-T log-p diagram with wind barbs and a hodograph.

    This function assumes that vertical profiles of pressure,
    temperature, dewpoint, and wind components have already
    been extracted and converted to physical units.

    Parameters
    ----------
    p : pint.Quantity
        Pressure profile [hPa].
    T : pint.Quantity
        Temperature profile [°C].
    Td : pint.Quantity
        Dewpoint temperature profile [°C].
    u : pint.Quantity
        Zonal wind profile [m s⁻¹].
    v : pint.Quantity
        Meridional wind profile [m s⁻¹].
    lat : float
        Latitude of the sounding location.
    lon : float
        Longitude of the sounding location.
    time : str
        Time of the sounding.
    savepath : str or pathlib.Path, optional
        Path where the generated PNG image will be saved.

    Returns
    -------
    matplotlib.figure.Figure
        The generated Matplotlib figure.
    """

    # initiate figure
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, rotation=45, rect=(0.1, 0.1, 0.55, 0.85))

    # plot temperature and dewpoint
    skew.plot(p, T, 'r', label='Temperature')
    skew.plot(p, Td, 'g', label='Dewpoint')

    # plot wind barbs
    skew.plot_barbs(p, u, v)

    # set axes limits
    skew.ax.set_xlim(-30, 40)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlabel('Temperature [°C]')
    skew.ax.set_ylabel('Pressure [hPa]')

    # set reference lines in skew T
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    # add hodograph
    ax_hod = plt.axes((0.75, 0.75, 0.2, 0.2))
    h = Hodograph(ax_hod, component_range=50.)
    h.add_grid(increment=10)
    h.plot(u, v)
    ax_hod.set_xlabel('Wind speed [m s$^{-1}$]')
    ax_hod.set_ylabel('Wind speed [m s$^{-1}$]')

    # set title
    skew.ax.set_title(
        f'Skew-T at {lat:.2f}°N, {lon:.2f}°E ({time})',
        fontsize=12
    )

    # save figure
    if savepath is not None:
        fig.savefig(savepath, bbox_inches='tight')
        plt.close(fig)

    return fig


def extract_vert_cross_section(
    param,
    u_param,
    v_param,
    start,
    end,
    time,
    datafile,
    npoints=200,
):
    """
    Extract data for a vertical cross section along a transect.

    Returns
    -------
    da_main : xarray.DataArray
        Main variable interpolated along transect (pressure, point)
    wind : xarray.DataArray
        Wind speed along transect (pressure, point)
    dist : ndarray
        Distance along transect in km
    """

    lat0, lon0 = start
    lat1, lon1 = end

    lats = np.linspace(lat0, lat1, npoints)
    lons = np.linspace(lon0, lon1, npoints)

    with xr.open_dataset(datafile) as ds:
        da_main = (
            ds[param]
            .sel(valid_time=time, method="nearest")
            .interp(latitude=("point", lats),
                    longitude=("point", lons))
        )

        u = (
            ds[u_param]
            .sel(valid_time=time, method="nearest")
            .interp(latitude=("point", lats),
                    longitude=("point", lons))
        )

        v = (
            ds[v_param]
            .sel(valid_time=time, method="nearest")
            .interp(latitude=("point", lats),
                    longitude=("point", lons))
        )

    wind = wind_speed(u.values * units("m/s"),
                      v.values * units("m/s")).magnitude

    # distance along transect
    dist = np.linspace(0, 1, npoints) * (
        111 * np.hypot(lat1 - lat0, lon1 - lon0)
    )

    wind = xr.DataArray(
        wind,
        dims=da_main.dims,
        coords=da_main.coords,
        name="wind_speed",
    )

    return da_main, wind, dist

    
def plot_vert_cross_section(
    da_main,
    wind_speed=None,
    dist=None,
    param="z",
    savepath=None,
):
    """
    Plot a vertical cross section with filled contours and dynamic wind levels.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if param == "t":
        cmap = "RdYlBu_r"  
        title_text = "Temperature (K)"
        plot_levels = np.linspace(float(da_main.min()), float(da_main.max()), 15)
    else:
        cmap = "viridis"   
        title_text = "Geopotential Height (m)"
        plot_levels = 20

    cf = ax.contourf(
        dist,
        da_main.pressure_level,
        da_main,
        levels=plot_levels,
        cmap=cmap,
        extend="both"
    )
    
    cbar = plt.colorbar(cf, ax=ax, orientation="vertical", pad=0.02)
    unit_label = "K" if param == "t" else "m"
    cbar.set_label(f"{title_text} [{unit_label}]")

    cs = ax.contour(
        dist,
        da_main.pressure_level,
        da_main,
        levels=10,
        colors="black",
        linewidths=0.5,
        alpha=0.3
    )
    ax.clabel(cs, fontsize=7, fmt="%.0f")

    # Highlight the Freezing Line if param is Temperature
    if param == "t":
        ax.contour(
            dist, da_main.pressure_level, da_main,
            levels=[273.15], colors="blue", linewidths=1.5, linestyles="--"
        )

    if wind_speed is not None:
        max_w = float(wind_speed.max())
        if max_w > 0.5:
            raw_levels = np.linspace(0, max_w, 6)[1:]
            dynamic_levels = np.unique(np.round(raw_levels * 2) / 2)

            csw = ax.contour(
                dist,
                wind_speed.pressure_level,
                wind_speed,
                levels=dynamic_levels,
                colors="red",
                linewidths=1.5,
            )
            ax.clabel(csw, fontsize=8, fmt="%g m/s")

    ax.invert_yaxis()
    ax.set_xlabel("Distance along transect (km)")
    ax.set_ylabel("Pressure (hPa)")
    ax.set_title(f"Vertical Cross Section: {title_text}")

    plt.tight_layout()

    if savepath is not None:
        fig.savefig(savepath, dpi=150, bbox_inches="tight")
        plt.close(fig)

    return fig
