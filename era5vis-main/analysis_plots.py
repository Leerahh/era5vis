'''
Updated by Lina Brückner, January 2026:
    - Adding plot_type
'''
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
    Generate an ERA5 model-level visualization (scalar_wind or skewT).

    Parameters
    ----------
    parameter : str
        ERA5 variable to plot (required for scalar_wind)
    level : int
        Pressure level in hPa (required for scalar_wind)
    time : str, optional
        Time to plot (YYYYmmddHHMM)
    time_index : int, optional
        Time index within dataset (used if `time` is None)
    plot_type : str, default "scalar_wind"
        Either "scalar_wind" or "skewT"
    download_data : bool, default False
        If True, download ERA5 data
    u1 : str, default "u"
        Horizontal wind component (scalar_wind only)
    u2 : str, default "v"
        Meridional wind component (scalar_wind only)
    lat : float, required for skewT
        Latitude (degrees)
    lon : float, required for skewT
        Longitude (degrees)
    directory : str or Path, optional
        Output directory for HTML/PNG
    no_browser : bool, default False
        If True, do not open a browser

    Returns
    -------
    Path
        Path to generated HTML file
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

    if not download_data:
        raise ValueError(
            "This command requires --download-data or download_data: true in the config."
        )

    # create cache once
    cache = Era5Cache()
    
    datafile = cache.get_analysis_plots_data(parameter, level, time=time)

    cfg.set_datafile(datafile)

    if plot_type == "scalar_wind":
        variables = [parameter, u1, u2]
        datafile = cache.get_analysis_plots_data(
            variables=variables,
            level=level,
            time=time,
        )

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

    elif plot_type == "skewT":
        variables = ["t", "q", "u", "v"]

        # ERA5 pressure levels for soundings
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


        html_path = core.write_skewT_html(
            lat=lat,
            lon=lon,
            time=time,
            datafile=datafile,
            directory=directory,
        )

    # open browser if requested
    if not no_browser:
        webbrowser.get().open_new_tab(f"file://{html_path}")
    else:
        print("File successfully generated at:", html_path)

    return html_path
