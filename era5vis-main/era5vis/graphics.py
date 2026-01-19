"""
Plot geopotential with wind barbs on a map. Plot SkewT diagram for selected location.
Updated by Lina Brückner, January 2026:
    - adding plot_scalar_with_wind and plot_skewT
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
    '''
    Plot scalar as contours and wind barbs on top.

    Parameters
    ----------
    da : xarray.DataArray
        Scalar field to plot (e.g., geopotential)
    u : xarray.DataArray
        Zonal wind component
    v : xarray.DataArray
        Meridional wind component
    filepath : str, optional
        If provided, the plot is saved to this path
    step : int, optional
        Subsampling step for wind barbs (default: 9)

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    '''

    if step < 1:  # prevent step=0
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
    “Extract a vertical thermodynamic and wind profile from ERA5 data.”

    Returns
    -------
    p : pint.Quantity
        Pressure profile [hPa]
    T : pint.Quantity
        Temperature profile [°C]
    Td : pint.Quantity
        Dewpoint profile [°C]
    u : pint.Quantity
        Zonal wind [m/s]
    v : pint.Quantity
        Meridional wind [m/s]
    """

    if variables is None:
        variables = {
            'T': 't',
            'q': 'q',
            'u': 'u',
            'v': 'v',
        }

    with xr.open_dataset(datafile) as ds:
        T_da = ds[variables['T']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest')

        q_da = ds[variables['q']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest')

        u_da = ds[variables['u']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest')

        v_da = ds[variables['v']] \
            .sel(latitude=lat, longitude=lon, method='nearest') \
            .sel(valid_time=time, method='nearest')

        # Pressure from the same DataArray
        p = T_da.pressure_level.values * units.hPa

        # Convert units
        T = (T_da.values * units.kelvin).to(units.degC)
        Td = mpcalc.dewpoint_from_specific_humidity(p, q_da.values).to(units.degC)
        u = u_da.values * units('m/s')
        v = v_da.values * units('m/s')

        # ERA5 is top-down → reverse for Skew-T
        p = p[::-1]
        T = T[::-1]
        Td = Td[::-1]
        u = u[::-1]
        v = v[::-1]

    return p, T, Td, u, v

def plot_skewT(p, T, Td, u, v, lat, lon, time, datafile=None, variables=None, savepath=None):
    """
    “Plot a Skew-T diagram from prepared profile data.”
    """

    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, rotation=45, rect=(0.1, 0.1, 0.55, 0.85))

    # Temperature & dewpoint
    skew.plot(p, T, 'r', label='Temperature')
    skew.plot(p, Td, 'g', label='Dewpoint')

    # Wind barbs
    skew.plot_barbs(p, u, v)

    # Axes limits
    skew.ax.set_xlim(-30, 40)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlabel('Temperature [°C]')
    skew.ax.set_ylabel('Pressure [hPa]')

    # Reference lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    # Hodograph
    ax_hod = plt.axes((0.75, 0.75, 0.2, 0.2))
    h = Hodograph(ax_hod, component_range=50.)
    h.add_grid(increment=10)
    h.plot(u, v)

    ax_hod.set_xlabel('Wind speed [m s$^{-1}$]')
    ax_hod.set_ylabel('Wind speed [m s$^{-1}$]')

    # Title
    skew.ax.set_title(
        f"Skew-T at {lat:.2f}°N, {lon:.2f}°E ({time})",
        fontsize=12
    )

    # Save or return
    if savepath is not None:
        fig.savefig(savepath, bbox_inches='tight')
        plt.close(fig)

    return fig
