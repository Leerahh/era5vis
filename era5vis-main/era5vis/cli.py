"""
Command line tools for ERA5vis.

Manuela Lehner
November 2025

Edited by Leah Herrfurth, December 2025:
    - Using argparse instead of sys.args
    - Adding config-based plotting
Edited by Lina Brückner, January 2026:
    - Adding parser arguments plot type and directory, u1, u2, lon and lat
    - Implementing new parser arguments in _merge_config_and_args()
"""

import era5vis
from . import core
from era5vis import analysis_plots
from pathlib import Path
import sys
import argparse
import yaml
import webbrowser



def analysis_plots(args):
    """Main entry function for the era5vis_analysis_plots CLI tool."""
    parsed_args = _parse_args(args)

    config = {}
    if parsed_args.config:
        config = _load_config(parsed_args.config)

    params = _merge_config_and_args(parsed_args, config)

    return era5vis.analysis_plots.run_analysis_plots(**params)


def era5vis_analysis_plots():
    """Entry point for the era5vis_analysis_plots application script."""
    analysis_plots(sys.argv[1:])


def _parse_args(args):
    """
    Parse command-line arguments for era5vis_analysis_plots.

    Parameters
    ----------
    args : list
        output of sys.argv[1:].

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="era5vis_analysis_plots",
        description="Visualization of ERA5 analysis plots."
    )

    parser.add_argument(
        "config",
        nargs="?",
        help="Path to configuration file."
    )
    parser.add_argument(
        "--v", "--version",
        action="version",
        version=(
            f"era5vis_analysis_plots: {era5vis.__version__}\n"
            "Licence: public domain\n"
            "era5vis_analysis_plots is provided 'as is' without warranty of any kind"
        )
    )
    parser.add_argument(
        "--p", "--parameter",
        dest="parameter",
        metavar="PARAM",
        help="ERA5 variable to plot (mandatory)"
    )
    parser.add_argument(
        "--lvl", "--level",
        dest="level",
        metavar="LEVEL",
        type=int,
        help="Pressure level to plot (hPa) (mandatory)"
    )
    parser.add_argument(
        "--t", "--time",
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
    parser.add_argument(
        "--pl", "--plot_type",
        dest="plot_type",
        choices=["scalar_wind", "skewT"],
        type=str,
        default="scalar_wind",
        help=("Select either scalar_wind or skewT"
        )
    )
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

    parser.add_argument(
        "--dd", "--download_data",
        dest="download_data",
        action="store_true",
        help=(
            "Download the needed ERA5 data for the specified parameter and level"
        )
    )

    if not args:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args([str(a) for a in args])


def _load_config(config_path):
    """
    Load configuration from a YAML file.

    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Configuration dictionary.
    """
    if not config_path.endswith((".yaml", ".yml")):
        raise ValueError("Config must be a .yaml or .yml file")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def _merge_config_and_args(args, config):
    """
    Merge command-line arguments with configuration file values.

    Command-line arguments take precedence over configuration.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.
    config : dict
        Loaded configuration dictionary.

    Returns
    -------
    dict
        Final parameters for plotting.
    """
    # determine plot type: CLI argument overrides YAML
    plot_type = args.plot_type or config.get("plot_type", "scalar_wind")

    # get plot-type-specific config section
    plot_config = config.get(plot_type, {}) if config else {}

    # get common config
    common_config = config.get("common", {}) if config else {}

    # merge CLI args with YAML: CLI overrides YAML
    params = {
        "plot_type": plot_type,
        "parameter": args.parameter or plot_config.get("parameter") or "z",
        "level": args.level or plot_config.get("level") or 500,
        "u1": getattr(args, "u", None) or plot_config.get("u") or "u",
        "u2": getattr(args, "v", None) or plot_config.get("v") or "v",
        "lat": getattr(args, "lat", None) or plot_config.get("lat"),
        "lon": getattr(args, "lon", None) or plot_config.get("lon"),
        "time": args.time or plot_config.get("time") or common_config.get("time"),
        "time_index": args.time_index or plot_config.get("time_index", 0),
        "directory": args.directory or common_config.get("directory", "."),
        "no_browser": args.no_browser or common_config.get("no_browser", False),
        "download_data": (
            args.download_data
            if args.download_data
            else common_config.get("download_data", True)
        ),
    }

    return params


#    req_dict = request.to_dict()  # if not available, build dict manually
#    hash = _request_hash(req_dict)

#    target = Path.cwd() / f"era5_{hash}.nc"

#    if target.exists():
#        print(f"Using cached ERA5 data: {target}")
#        return target

#    print("Downloading ERA5 data...")
#    download_era5_data(request.to_dict(), target=target)
#    if not target.exists():
#        raise RuntimeError(
#            f"ERA5 download reported success but file was not found: {target}"
#        )
#    return target
