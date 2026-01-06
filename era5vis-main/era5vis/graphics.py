"""Plot geopotential with wind barbs on a map and Skew-T diagram for example location."""

from datetime import datetime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import xarray as xr
from metpy.plots import SkewT, Hodograph
from metpy.units import units
import metpy.calc as mpcalc

def plot_geopotential_with_wind(da, u, v, filepath=None, step=1):
    '''Plot geopotential as contours and wind barbs on top.

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

    # plot geopotential as filled contours
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
        #length=6,
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

    if filepath is not None:
        fig.savefig(filepath, bbox_inches='tight')
        plt.close()

    return fig


def plot_skewT(lat, lon, time, datafile, variables=None, savepath=None, curve=None):
    '''
    Plot a full Skew-T diagram for a given location and time from ERA5 data,
    including temperature, dewpoint, wind barbs, reference lines, and optional curve.

    Parameters
    ----------
    lat, lon : float
        Latitude and longitude of the sounding
    time : str
        Time string, e.g., '2026-01-06T00:00'
    datafile : str
        Path to ERA5 NetCDF file
    variables : dict, optional
        Mapping of variables in the dataset, e.g.,
        {'T': 't2m', 'Td': 'd2m', 'u': 'u10', 'v': 'v10', 'p': 'msl'}
    savepath : str, optional
        Path to save figure
    curve : dict, optional
        Optional curve to overlay, e.g.,
        {'p': pressure_array, 'T': temperature_array, 'label': 'Parcel Path', 'color': 'purple'}
    '''

    # default variable names
    if variables is None:
        variables = {
            'T': 't2m',    # temperature
            'q': 'q',    # specific humidity
            'u': 'u',    # zonal wind
            'v': 'v',    # meridional wind
            'p': 'pressure_level'    # vertical pressure coordinate
            }

    with xr.open_dataset(datafile) as ds:
    # select nearest lat/lon
        T = ds['t'].sel(latitude=lat, longitude=lon, method='nearest').sel(valid_time=time, method='nearest')
        q = ds['q'].sel(latitude=lat, longitude=lon, method='nearest').sel(valid_time=time, method='nearest')
        u = ds['u'].sel(latitude=lat, longitude=lon, method='nearest').sel(valid_time=time, method='nearest')
        v = ds['v'].sel(latitude=lat, longitude=lon, method='nearest').sel(valid_time=time, method='nearest')
        p = ds['pressure_level']

    T = T.values * units.kelvin
    u = u.values * units('m/s')
    v = v.values * units('m/s')
    p = p.values * units.hPa
    
    if 'Td' in variables:
        Td = ds[variables['Td']].sel(latitude=lat, longitude=lon, method='nearest').sel(valid_time=time, method='nearest')
        Td = Td.values * units.kelvin
    else:
        # compute from specific humidity
        q = ds[variables['q']].sel(latitude=lat, longitude=lon, method='nearest').sel(valid_time=time, method='nearest')
        Td = mpcalc.dewpoint_from_specific_humidity(p, q)

    # create figure
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, rotation=45, rect=(0.1, 0.1, 0.55, 0.85))

    # plot temperature and dewpoint
    skew.plot(p, T, 'r', label='Temperature')
    skew.plot(p, Td, 'g', label='Dewpoint')

    # plot wind barbs
    skew.plot_barbs(p, u, v)

    # set plot limits
    skew.ax.set_xlim(-30, 40)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlabel('Temperature [°C]')
    skew.ax.set_ylabel('Pressure [hPa]')

    # Add reference lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    # create a Hodograph inset
    ax_hod = plt.axes((0.7, 0.75, 0.2, 0.2))
    h = Hodograph(ax_hod, component_range=50.)
    h.add_grid(increment=10)
    h.plot(u, v)
    ax_hod.set_xlabel('Wind speed [m s$^{-2}$]')

    # title
    skew.ax.set_title(f'Skew-T at {lat:.2f}N, {lon:.2f}E ({time})', fontsize=12)

    if savepath is not None:
        fig.savefig(savepath, bbox_inches='tight')
        plt.close(fig)

    return fig


if __name__ == '__main__':
    '''
    Test plotting functions in graphics.py.

    This script tests:
    1) Horizontal geopotential + wind barbs map
    2) Vertical Skew-T diagram at a selected location

    Requires a valid ERA5 NetCDF dataset.
    '''

    from era5vis.era5 import check_file_availability, horiz_cross_section

    # Check ERA5 dataset
    check_file_availability()
    datafile = r'data\era5_example_1.nc'

    # map plot settings
    level = 850
    time_index = 0

    # Skew-T settings
    lat, lon = 50.0, 10.0
    time = '2025-10-01T00:00'

    # map plot (geopotential + wind)
    da = horiz_cross_section('z', level, time_index)
    u = horiz_cross_section('u', level, time_index)
    v = horiz_cross_section('v', level, time_index)

    plot_geopotential_with_wind(
        da, u, v,
        filepath=f'geopotential_wind_{level}hPa.png',
        step=9
    )

    # Skew-T plot
    plot_skewT(
        lat=lat,
        lon=lon,
        time=time,
        datafile=datafile,
        savepath='skewT_example.png'
    )
