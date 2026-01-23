"""
Core orchestration utilities for ERA5 visualizations.

This module provides helper functions that connect ERA5 data
access, plotting routines, and HTML generation. It acts as the glue
between:

- data validation and extraction (``era5``)
- plotting functions (``graphics``)
- HTML templating and file output (``cfg``)

The functions in this module do not perform any data downloading
themselves and require an explicit ERA5 data file to be provided.

Updated by Lina Brückner, January 2026:
    - Added HTML writers for scalar-with-wind maps and Skew-T diagrams
    - Removed usage of example data files (explicit datafile required)
"""

from pathlib import Path
from tempfile import mkdtemp
import shutil

from era5vis import cfg, graphics, era5
from era5vis.data_access import download_era5


def mkdir(path, reset=False):
    """
    Create a directory if it does not already exist.

    Optionally removes an existing directory and recreates it.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the directory.
    reset : bool, default False
        If True and the directory already exists, delete its contents
        before recreating it.

    Returns
    -------
    pathlib.Path
        Path to the created (or existing) directory.
"""

    # if requested, remove the directory and all its components
    if reset and Path.is_dir(path):
          shutil.rmtree(path)
    # attempt to create the directory
    try:
        Path.mkdir(path, parents=True)
    except FileExistsError:
        # directory already exists and reset=False
        pass
    return path


def write_scalar_with_wind_html(
    scalar, u, v, level, time=None, time_index=None, directory=None, step=9, datafile=None
):
    """
    Generate an HTML page containing a scalar field map with wind vectors.

    This function:
    1. Validates the requested ERA5 data
    2. Extracts a horizontal cross section
    3. Generates a PNG plot
    4. Embeds the plot into an HTML template

    Parameters
    ----------
    scalar : str
        ERA5 scalar variable to plot (e.g. ``"z"``, ``"t"``).
    u : str
        ERA5 zonal wind variable name.
    v : str
        ERA5 meridional wind variable name.
    level : int
        Pressure level in hPa.
    time : str, optional
        Datetime string compatible with ERA5 ``valid_time``.
    time_index : int, optional
        Time index used if ``time`` is None.
    directory : str or pathlib.Path, optional
        Output directory for the generated PNG and HTML files.
        If None, a temporary directory is created.
    step : int, default 9
        Subsampling step for wind vectors.
    datafile : str or pathlib.Path
        Path to the ERA5 NetCDF data file.

    Returns
    -------
    pathlib.Path
        Path to the generated HTML file.

    Raises
    ------
    ValueError
        If no datafile is provided.
    """

    # fallback to time index if no explicit time is provided
    if time is None:
        time = time_index

    # explicit datafile is required (example files are no longer supported)
    if datafile is None:
        raise ValueError(
        "datafile must be provided explicitly; example files are no longer used"
        )


    # check that dataset exists abd contains the required variables
    era5.check_file_availability(datafile)
    for var in (scalar, u, v):
        era5.check_data_availability(var, level=level, time=time, datafile=datafile)

    # create a temporary output directory if necessary
    if directory is None:
        directory = mkdtemp()
    mkdir(directory)

    print('Extracting data')

    # extract horizontal cross sections for scalar and wind components
    da = era5.horiz_cross_section(scalar, level, time, datafile)
    u_da = era5.horiz_cross_section(u, level, time, datafile)
    v_da = era5.horiz_cross_section(v, level, time, datafile)

    print('Plotting data')

    # create a filename-safe timestamp
    time_safe = str(time).replace(':', '-').replace(' ', '_')
    png = Path(directory) / f'scalar_wind_{scalar}_{level}_{time_safe}.png'

    # generate PNG plot
    graphics.plot_scalar_with_wind(
        da, u_da, v_da, savepath=png, step=step
    )

    # create HTML output using the template
    outpath = Path(directory) / 'index.html'
    with open(cfg.html_template) as infile:
        template = infile.read()

    html = (
        template
        .replace('[PLOTTYPE]', 'Scalar field with wind')
        .replace('[PLOTVAR]', scalar)
        .replace('[IMGTYPE]', png.name)
    )

    with open(outpath, 'w') as infile:
        infile.write(html)

    return outpath

def write_skewT_html(
    lat, lon, time, datafile=None, directory=None, **kwargs
):
    """
    Generate an HTML page containing a Skew-T diagram for a given location.

    This function:
    1. Extracts a vertical ERA5 profile
    2. Generates a Skew-T PNG plot
    3. Embeds the plot into an HTML template

    Parameters
    ----------
    lat : float
        Latitude of the sounding location (degrees).
    lon : float
        Longitude of the sounding location (degrees).
    time : str
         Datetime string compatible with ERA5 ``valid_time``.
    datafile : str or pathlib.Path
        Path to the ERA5 NetCDF data file.
    directory : str or pathlib.Path, optional
        Output directory for the generated PNG and HTML files.
        If None, a temporary directory is created.

    Returns
    -------
    pathlib.Path
        Path to the generated HTML file.

    Raises
    ------
    ValueError
        If no datafile is provided.
    """

    # explicit datafile is required
    if datafile is None:
        raise ValueError(
        "datafile must be provided explicitly; example files are no longer used"
        )

    # create temporary output directory if necessary
    if directory is None:
        directory = mkdtemp()
    mkdir(directory)

    print('Plotting Skew-T')

    # create a filename-safe timestamp
    time_safe = str(time).replace(':', '-').replace(' ', '_')
    png = Path(directory) / f'SkewT_{lat:.2f}_{lon:.2f}_{time_safe}.png'

    # extract vertical profile data
    p, T, Td, u, v = graphics.extract_skewT_profile(
        lat=lat,
        lon=lon,
        time=time,
        datafile=datafile,
    )

    # generate PNG plot
    graphics.plot_skewT(
        p, T, Td, u, v,
        lat=lat,
        lon=lon,
        time=time,
        savepath=png,
    )

    # generate HTML output using the template
    outpath = Path(directory) / 'index.html'
    with open(cfg.html_template, 'r') as infile:
        lines = infile.readlines()

    out = []
    for txt in lines:
        txt = txt.replace('[PLOTTYPE]', 'Skew-T diagram')
        txt = txt.replace('[PLOTVAR]', f'{lat:.2f}°, {lon:.2f}° @ {time}')
        txt = txt.replace('[IMGTYPE]', png.name)
        out.append(txt)

    with open(outpath, 'w') as outfile:
        outfile.writelines(out)

    return outpath

def write_vert_cross_html(
    param, start, end, time, u='u', v='v', npoints=200, datafile=None, directory=None,
):
    """
    Generate an HTML page containing a vertical cross section plot.
    """

    if datafile is None:
        raise ValueError(
        "datafile must be provided explicitly; example files are no longer used"
        )

    era5.check_file_availability(datafile)
    era5.check_data_availability(param, time=time, datafile=datafile)

    if directory is None:
        directory = mkdtemp()
    mkdir(directory)

    print("Plotting vertical cross section")

    time_safe = str(time).replace(":", "-").replace(" ", "_")
    png = Path(directory) / f"vert_cross_{param}_{time_safe}.png"

    da_main, wind_speed, dist = graphics.extract_vert_cross_section(
        param=param,
        u_param=u,
        v_param=v,
        start=start,
        end=end,
        time=time,
        npoints=npoints,
        datafile=datafile,
    )

    graphics.plot_vert_cross_section(
        da_main=da_main,
        wind_speed=wind_speed,
        dist=dist,
        param=param,
        savepath=png,
    )

    outpath = Path(directory) / "index.html"
    with open(cfg.html_template) as infile:
        template = infile.read()

    html = (
        template
        .replace("[PLOTTYPE]", "Vertical cross section")
        .replace("[PLOTVAR]", param)
        .replace("[IMGTYPE]", png.name)
    )

    with open(outpath, "w") as infile:
        infile.write(html)

    return outpath
