"""
Interface for generating ERA5 analysis plots.

This module provides the main public API function used by both the
command-line interface and programmatic usage. It orchestrates:

- validation of user input
- retrieval and caching of ERA5 data
- delegation to plotting and HTML generation routines
- optional automatic display of results in a web browser

Author: Leah Herrfurth
Updated by Lina Brückner, January 2026:
    - Added support for multiple plot types (scalar_wind, skewT)
"""

import webbrowser
from era5vis.data_access.era5_cache import Era5Cache
from era5vis import core, cfg

def run_analysis_plots(
    parameter=None,
    level=None,
    time=None,
    time_index=0,
    plot_type="scalar_wind",
    download_data=False,
    u1="u",
    u2="v",
    lat=None,
    lon=None,
    directory=None,
    no_browser=False,
):
    """
    Generate an ERA5 analysis visualization and corresponding HTML output.

    This function serves as the main high-level entry point for ERA5vis.
    Depending on the selected ``plot_type``, it generates either:

    - a horizontal scalar field plot with wind vectors
    - a Skew-T diagram for a specified location

    Internally, the function handles ERA5 data retrieval via a cache,
    delegates plotting to the ``core`` and ``graphics`` modules, and
    optionally opens the result in a web browser.

    Parameters
    ----------
    parameter : str, optional
        ERA5 scalar variable to plot (e.g. ``"z"``, ``"t"``).
        Required for ``plot_type="scalar_wind"``.
    level : int, optional
        Pressure level in hPa.
        Required for ``plot_type="scalar_wind"``.
    time : str, optional
        Datetime string compatible with ERA5 ``valid_time``
        (format: ``YYYYmmddHHMM``).
        Required for ``plot_type="skewT"``.
    time_index : int, default 0
        Time index within the dataset, used if ``time`` is None.
    plot_type : {"scalar_wind", "skewT"}, default "scalar_wind"
        Type of visualization to generate.
    download_data : bool, default False
        If True, download ERA5 data if not already cached.
        Must be True for this function to run.
    u1 : str, default "u"
        ERA5 zonal (east–west) wind component variable name
        (scalar_wind only).
    u2 : str, default "v"
        ERA5 meridional (north–south) wind component variable name
        (scalar_wind only).
    lat : float, optional
        Latitude in degrees.
        Required for ``plot_type="skewT"``.
    lon : float, optional
        Longitude in degrees.
        Required for ``plot_type="skewT"``.
    directory : str or pathlib.Path, optional
        Output directory for generated PNG and HTML files.
        If None, a temporary directory is used.
    no_browser : bool, default False
        If True, do not automatically open the generated HTML file
        in a web browser.

    Returns
    -------
    pathlib.Path
        Path to the generated HTML file.

    Raises
    ------
    ValueError
        If required parameters for the selected plot type are missing.
    ValueError
        If an unknown ``plot_type`` is specified.
    """
    

    # validate required parameters
    if plot_type == "scalar_wind":
        if parameter is None or level is None:
            raise ValueError("For scalar_wind, 'parameter' and 'level' are required.")
    elif plot_type == "skewT":
        if lat is None or lon is None or time is None:
            raise ValueError("For skewT, 'lat', 'lon', and 'time' are required.")
    else:
        raise ValueError(f"Unknown plot_type '{plot_type}'.")

    # decide data source
    use_example_data = not download_data

    # select datafile
    if use_example_data:
        # Use packaged example datasets
        if plot_type == "scalar_wind":
            datafile = cfg.scalar_wind_datafile
        else:  # skewT
            datafile = cfg.skewT_datafile

    else:
        # download / cache real ERA5 data
        cache = Era5Cache()

        if plot_type == "scalar_wind":
            variables = [parameter, u1, u2]

            datafile = cache.get_analysis_plots_data(
                variables=variables,
                level=level,
                time=time,
            )

        else:  # skewT
            variables = ["t", "q", "u", "v"]
            levels = [
                1000, 975, 950, 925, 900, 875, 850, 825, 800,
                775, 750, 700, 650, 600, 550, 500, 450, 400,
                350, 300, 250, 200, 150, 100
            ]

            datafile = cache.get_analysis_plots_data(
                variables=variables,
                level=levels,
                time=time,
            )

    # make datafile globally available
    cfg.set_datafile(datafile)

    # Generate plot and HTML
    if plot_type == "scalar_wind":
        html_path = core.write_scalar_with_wind_html(
            scalar=parameter,
            u=u1,
            v=u2,
            level=level,
            time=time,
            time_index=time_index,
            directory=directory,
            datafile=datafile,
        )

    else:  # skewT
        html_path = core.write_skewT_html(
            lat=lat,
            lon=lon,
            time=time,
            datafile=datafile,
            directory=directory,
        )

    # open browser or print path
    if not no_browser:
        webbrowser.get().open_new_tab(f"file://{html_path}")
    else:
        print("File successfully generated at:", html_path)

    return html_path
