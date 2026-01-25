"""
Command-line interface (CLI) for ERA5vis analysis plots.

This module defines the ``era5vis_analysis_plots`` command-line tool, which
allows users to generate ERA5 visualizations directly from the terminal.
The CLI supports:

- scalar field plots with wind vectors
- Skew-T diagrams at a selected location
- vertical cross section plots
- configuration via YAML files
- command-line overrides of configuration options

The CLI acts as a thin wrapper around the plotting API in ``analysis_plots``
and ``core``.

Authors
-------
Manuela Lehner, November 2025

Edits
-----
Leah Herrfurth, December 2025
    - Switched from manual ``sys.argv`` parsing to ``argparse``
    - Added config-based plotting

Lina Brückner, January 2026
    - Added parser arguments plot type, directory, wind component and location arguments
    - Integrated new arguments into configuration merging logic
    - Integrated fallback to example ERA5 datasets in ./data if downloading is disabled

Leah Herrfurth, January 2026
    - Added data download Elements
    - Refactoring 
    - Storing logic for analysis_plots outside
"""

import era5vis
from era5vis import analysis_plots as analysis_plots_api
import sys
import argparse
import yaml
from era5vis.utils.cli_or_config import cli_or_config


def analysis_plots(args):
    """
    Main entry function for the ``era5vis_analysis_plots`` CLI tool.

    This function:
    1. Parses command-line arguments
    2. Loads an optional YAML configuration file
    3. Merges command-line arguments with configuration values
    4. Executes the analysis plotting routine

    Parameters
    ----------
    args : list of str
        Command-line arguments (typically ``sys.argv[1:]``).

    Returns
    -------
    pathlib.Path
        Path to the generated HTML file.
    """

    parsed_args = _parse_args(args)

    # load configuration file if provided
    config = {}
    if parsed_args.config:
        config = _load_config(parsed_args.config)

    # merge CLI arguments and configuration values
    params = _merge_config_and_args(parsed_args, config)

    return era5vis.analysis_plots.run_analysis_plots(**params)


def era5vis_analysis_plots():
    """
    Entry point for the ``era5vis_analysis_plots`` console script.

    This function is intended to be registered as a console entry point
    and forwards command-line arguments to :func:`analysis_plots`.
    """
    
    analysis_plots(sys.argv[1:])


def _parse_args(args):
    """
    Parse command-line arguments for ``era5vis_analysis_plots``.

    Parameters
    ----------
    args : list of str
        Command-line arguments (typically ``sys.argv[1:]``).

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="era5vis_analysis_plots",
        description="Visualization of ERA5 analysis plots."
    )
    # optional YAML configuration file
    parser.add_argument(
        "config",
        nargs="?",
        help="Path to configuration file."
    )
    # version information
    parser.add_argument(
        "--v", "--version",
        action="version",
        version=(
            f"era5vis_analysis_plots: {era5vis.__version__}\n"
            "Licence: public domain\n"
            "era5vis_analysis_plots is provided \"as is\" without warranty of any kind"
        )
    )
    
    # scalar variable
    parser.add_argument(
        "--p", "--parameter",
        dest="parameter",
        metavar="PARAM",
        help="ERA5 variable to plot (mandatory)"
    )
    # pressure level
    parser.add_argument(
        "--lvl", "--level",
        dest="level",
        metavar="LEVEL",
        type=int,
        help="Pressure level to plot (hPa) (mandatory)"
    )
    
    # time selection
    parser.add_argument(
        "-t", "--time",
        dest="time",
        metavar="TIME",
        help="Time to plot (YYYYmmddHHMM)"
    )
    parser.add_argument(
        "--ti", "--time_index",
        dest="time_index",
        metavar="TIME_IND",
        type=int,
        default=0,
        help=(
            "Time index within dataset to plot (--time takes precedence "
            "if both --time and --time_index are specified) (default=0)"
        )
    )

    # plot type
    parser.add_argument(
        "--pl", "--plot_type",
        dest="plot_type",
        choices=["scalar_wind", "skewT", "vert_cross"],
        type=str,
        default="scalar_wind",
        help=("Select plot type: scalar_wind, skewT or vert_cross"
        )
    )

    # output handling
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help=(
            "Do not open a browser with the newly generated visualization, "
            "just print the path to the HTML file instead"
        )
    )
    parser.add_argument(
        "--directory",
        metavar="DIR",
        help=("Directory where the HTML file will be saved (overrides config)"
        )
    )

    # wind components
    parser.add_argument(
        "--u1", "--horizontal_wind",
        dest="u",
        help=("Horizontal wind component in m s$^{-1}$"
        )
    )
    parser.add_argument(
        "--u2", "--meridional_wind",
        dest="v",
        help=("Meridional wind component in m s$^{-1}$"
        )
    )

    # location for skew-T plots
    parser.add_argument(
        "--lat", "--latitude",
        dest="lat",
        type=float,
        help=("Latitude in degrees"
        )
    )
    parser.add_argument(
        "--lon", "--longitude",
        dest="lon",
        type=float,
        help=("Longitude in degrees"
        )
    )

    # transect for vertical cross sections
    parser.add_argument(
        "--lat0",
        dest="lat0",
        type=float,
        help="Start latitude of transect"
    )
    parser.add_argument(
        "--lon0",
        dest="lon0",
        type=float,
        help="Start longitude of transect"
    )
    parser.add_argument(
        "--lat1",
        dest="lat1",
        type=float,
        help="End latitude of transect"
    )
    parser.add_argument(
        "--lon1",
        dest="lon1",
        type=float,
        help="End longitude of transect"
    )
    parser.add_argument(
        "--npoints",
        dest="npoints",
        type=int,
        default=200,
        help="Number of interpolation points along transect"
    )

    parser.add_argument(
        "--df", "--datafile",
        dest="datafile",
        help=("Path to ERA5 data file (overrides config)")
    )

    # data download flag
    parser.add_argument(
        "--dd", "--download_data",
        dest="download_data",
        action="store_true",
        help=(
            "Download ERA5 data from CDS. "
            "If not set, packaged example data are used."
        )
    )

    # print help and exit if no arguments are provided
    if not args:
        parser.print_help()
        raise SystemExit(0)

    return parser.parse_args([str(a) for a in args])


def _load_config(config_path):
    """
    Load plotting configuration from a YAML file.

    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Parsed configuration dictionary.

    Raises
    ------
    ValueError
        If the file extension is not ``.yaml`` or ``.yml``.
    """

    if not config_path.endswith((".yaml", ".yml")):
        raise ValueError("Config must be a .yaml or .yml file")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _merge_config_and_args(args, config):
    """
    Merge command-line arguments with configuration file values.

    Command-line arguments always take precedence over configuration
    file values.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.
    config : dict
        Configuration dictionary loaded from YAML.

    Returns
    -------
    dict
        Final parameter dictionary passed to the plotting API.
    """

    # determine plot type (CLI argument overrides configuration)
    plot_type = args.plot_type or config.get("plot_type", "scalar_wind")

    # get plot-type-specific configuration section
    plot_config = config.get(plot_type, {}) if config else {}

    # merge CLI args with YAML (CLI arguments override configuration)
    params = {
        "plot_type": plot_type,
        "parameter": cli_or_config(args.parameter, plot_config.get("parameter")),
        "level": cli_or_config(args.level, plot_config.get("level")),
        "u1": cli_or_config(args.u, plot_config.get("u"), "u"),
        "u2": cli_or_config(args.v, plot_config.get("v"), "v"),
        "lat": cli_or_config(args.lat, plot_config.get("lat")),
        "lon": cli_or_config(args.lon, plot_config.get("lon")),
        "lat0": cli_or_config(args.lat0, plot_config.get("lat0")),
        "lon0": cli_or_config(args.lon0, plot_config.get("lon0")),
        "lat1": cli_or_config(args.lat1, plot_config.get("lat1")),
        "lon1": cli_or_config(args.lon1, plot_config.get("lon1")),
        "time": cli_or_config(args.time, plot_config.get("time"), "2025-10-01T00:00"),
        "npoints": cli_or_config(args.npoints, plot_config.get("npoints"), 200),
        "time_index": cli_or_config(args.time_index, plot_config.get("time_index"), 0),
        "directory": cli_or_config(args.directory, config.get("directory"), "."),
        "datafile": cli_or_config(args.datafile, config.get("datafile")),
        "no_browser": cli_or_config(args.no_browser, config.get("no_browser"), False),
        "download_data": cli_or_config(args.download_data, config.get("download_data"), False),
    }

    return params
