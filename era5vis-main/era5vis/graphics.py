"""
Plotting utilities for ERA5 visualizations.

This module provides functions to visualize ERA5 pressure-level data,
including:

- Horizontal maps of scalar fields with overlaid wind vectors
- Vertical atmospheric soundings using Skew-T diagrams with hodographs

The functions in this module assume that ERA5 data follow standard
naming conventions (e.g. ``pressure_level``, ``valid_time``,
``latitude``, ``longitude``) and are provided either as
``xarray.DataArray`` objects or via ERA5 NetCDF files.

Updated by Lina Brückner, January 2026:
    - Added scalar-with-wind map plotting
    - Added Skew-T and hodograph plotting utilities
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

def plot_scalar_with_wind(da, u, v, savepath=None, step=9):
    """
    Plot a horizontal scalar field with wind vectors on a map.

    The scalar field is displayed using filled contours, while wind
    vectors are overlaid using quivers on a Plate Carrée projection.

    Parameters
    ----------
    da : xarray.DataArray
        Scalar field to plot (e.g. geopotential or temperature).
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
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()

    # save figure
    if savepath is None:
        time_safe = str(time).replace(":", "-").replace(" ", "_")
        filename = f"scalar_wind_{da.name}_{da.pressure_level.to_numpy()}_{time_safe}.png"
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
    is computed from specific humidity using MetPy.Pressure levels
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
        Defaults to ``{'T': 't', 'q': 'q', 'u': 'u', 'v': 'v'}``.

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
            .sel(valid_time=time, method='nearest')

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

    This function assumes that pressure, temperature, dewpoint,
    and wind profiles have already been extracted and converted
    to physical units.

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
        f"Skew-T at {lat:.2f}°N, {lon:.2f}°E ({time})",
        fontsize=12
    )

    # save figure
    if savepath is not None:
        fig.savefig(savepath, bbox_inches='tight')
        plt.close(fig)

    return fig
