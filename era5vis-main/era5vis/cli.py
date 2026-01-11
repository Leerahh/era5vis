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
    - Updating _generate_plot() for the two different plot types
"""

import sys
import webbrowser
import argparse
import yaml
import era5vis
from . import core
import hashlib
import json
from pathlib import Path
from era5vis.data_access.download_era5 import download_era5_data
from era5vis.data_access.era5_request import Era5Request


def analysis_plots(args):
    """Main entry function for the era5vis_analysis_plots CLI tool."""
    parsed_args = _parse_args(args)

    config = {}
    if parsed_args.config:
        config = _load_config(parsed_args.config)

    params = _merge_config_and_args(parsed_args, config)

    _generate_plot(**params)


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
        "-v", "--version",
        action="version",
        version=(
            f"era5vis_analysis_plots: {era5vis.__version__}\n"
            "Licence: public domain\n"
            "era5vis_analysis_plots is provided 'as is' without warranty of any kind"
        )
    )
    parser.add_argument(
        "-p", "--parameter",
        metavar="PARAM",
        help="ERA5 variable to plot (mandatory)"
    )
    parser.add_argument(
        "-lvl", "--level",
        metavar="LEVEL",
        type=int,
        help="Pressure level to plot (hPa) (mandatory)"
    )
    parser.add_argument(
        "-t", "--time",
        metavar="TIME",
        help="Time to plot (YYYYmmddHHMM)"
    )
    parser.add_argument(
        "-ti", "--time_index",
        metavar="TIME_IND",
        type=int,
        default=0,
        help=(
            "Time index within dataset to plot (--time takes precedence "
            "if both --time and --time_index are specified) (default=0)"
        )
    )
    parser.add_argument(
        "-pl", "--plot_type",
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
        "-u1", "--horizontal_wind",
        dest="u",
        help=("Horizontal wind component in m s$^{-1}$"
        )
    )
    parser.add_argument(
        "-u2", "--meridional_wind",
        dest="v",
        help=("Meridional wind component in m s$^{-1}$"
        )
    )
    parser.add_argument(
        "-lat", "--latitude",
        help=("Latitude in degrees"
        )
    )
    parser.add_argument(
        "-lon", "--longitude",
        help=("Longitude in degrees"
        )
    )

    parser.add_argument(
        "--download-data",
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
        "download_data": args.download_data or plot_config.get("download_data", False),
  }

    return params

def _download_era5_data(parameter, level, time=None, time_index=0):
    """
    Download ERA5 data for the specified parameter and level.

    Parameters
    ----------
    parameter : str
        ERA5 variable to download.
    level : int
        Pressure level in hPa.
    time : str, optional
        Time to download (YYYYmmddHHMM), by default None
    """

    request = Era5Request(
        product_type=["reanalysis"],
        variable=[parameter],
        year=[time[0:4]] if time else ["2025"],
        month=[time[4:6]] if time else ["03"],
        day=[time[6:8]] if time else ["02", "03", "04"],
        time=[f"{time[8:10]}:00"] if time else [
            "00:00", "01:00", "02:00",
            "03:00", "04:00", "05:00",
            "06:00", "07:00", "08:00",
            "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00",
            "15:00", "16:00", "17:00",
            "18:00", "19:00", "20:00",
            "21:00", "22:00", "23:00"
        ],
        pressure_level=[str(level)],
        data_format="netcdf",
        download_format="unarchived",
        area=[70, -20, -30, 50]
    )


    req_dict = request.to_dict()  # if not available, build dict manually
    hash = _request_hash(req_dict)

    target = Path.cwd() / f"era5_{hash}.nc"

    if target.exists():
        print(f"Using cached ERA5 data: {target}")
        return target

    print("Downloading ERA5 data...")
    download_era5_data(request.to_dict(), target=target)
    if not target.exists():
        raise RuntimeError(
            f"ERA5 download reported success but file was not found: {target}"
        )
    return target


def _generate_plot(params, level, time=None, time_index=0, no_browser=False, download_data=False):
    """
    Generate an ERA5 visualization and optionally open it in a browser.

    Parameters
    ----------
    parameter : str
        ERA5 variable to plot.
    level : int
        Pressure level in hPa.
    time : str, optional
        Time to plot (YYYYmmddHHMM), by default None
    time_index : int, optional
        Time index to plot, by default 0
    plot_type : str, optional
        Type of plot: "scalar_wind" (default) or "skewT"
    no_browser : bool, optional
        If True, do not open the browser, by default False
    directory : str, optional
        Directory where the HTML file will be saved (overrides config)
    horizontal_wind: float, required for scalar_wind
        Horizontal wind component in m s$^{-1}$
    meridional_wind: float, required for scalar_wind
        Meridional wind component in m s$^{-1}$
    latitude: float, required for skewT
        Latitude in degrees
    longitude: float, required for skewT
        Longitude in degrees
    """
    
    datafile = None
    if download_data:
        datafile = _download_era5_data(
            parameter=params["parameter"],
            level=level,
            time=time,
            time_index=time_index
        )
    else: 
        datafile = era5vis.cfg.example_datafile
    era5vis.cfg.set_datafile(datafile)


    plot_type = params.get("plot_type", "scalar_wind")

    # define required parameters according to plot type
    if plot_type == "scalar_wind":
        required = ["parameter", "level", "u1", "u2"]
        missing = [k for k in required if k not in params or params[k] is None]
        if missing:
            raise ValueError(f"For scalar_wind plots, missing: {', '.join(missing)}")

        html_path = core.write_scalar_with_wind_html(
            scalar=params["parameter"],
            u=params["u1"],
            v=params["u2"],
            level=params["level"],
            time=params.get("time"),
            time_index=params.get("time_index", 0),
            directory=params.get("directory"),
        )

    elif plot_type == "skewT":
        required = ["lat", "lon", "time"]
        missing = [k for k in required if k not in params or params[k] is None]
        if missing:
            raise ValueError(f"For skewT plots, missing: {', '.join(missing)}")

        html_path = core.write_skewT_html(
            lat=params["lat"],
            lon=params["lon"],
            time=params["time"],
            directory=params.get("directory"),
        )

    else:
        raise ValueError(f"Unknown plot_type '{plot_type}' specified.")

    if params.get("no_browser", False):
        print("File successfully generated at:", html_path)
    else:
        webbrowser.get().open_new_tab(f"file://{html_path}")



def _request_hash(request: dict) -> str:
    payload = json.dumps(request, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]
