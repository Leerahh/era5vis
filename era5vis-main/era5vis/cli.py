"""
Command line tools for ERA5vis.

Manuela Lehner
November 2025

Edited by Leah Herrfurth, December 2025:
    - Using argparse instead of sys.args
    - Adding config-based plotting
Edited by Lina Brückner, January 2026:
    - Adding parser arguments plot type and directory
    - Adding new parser arguments in _merge_config_and_args()
    - Update of _generate_plot() for the two different plot types
"""

import sys
import webbrowser
import argparse
import yaml
import era5vis
from . import core




def modellevel(args):
    """Main entry function for the era5vis_modellevel CLI tool."""
    parsed_args = _parse_args(args)

    config = {}
    if parsed_args.config:
        config = _load_config(parsed_args.config)

    params = _merge_config_and_args(parsed_args, config)

    _generate_plot(**params)


def era5vis_modellevel():
    """Entry point for the era5vis_modellevel application script."""
    modellevel(sys.argv[1:])


def _parse_args(args):
    """
    Parse command-line arguments for era5vis_modellevel.

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
        prog="era5vis_modellevel",
        description="Visualization of ERA5 at a given model level."
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
            f"era5vis_modellevel: {era5vis.__version__}\n"
            "Licence: public domain\n"
            "era5vis_modellevel is provided 'as is' without warranty of any kind"
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
        "--plot_type",
        choices=["scalar_wind","skewT"],
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
        "parameter": args.parameter or plot_config.get("parameter"),
        "level": args.level or plot_config.get("level"),
        "u": getattr(args, "u", None) or plot_config.get("u"),
        "v": getattr(args, "v", None) or plot_config.get("v"),
        "lat": getattr(args, "lat", None) or plot_config.get("lat"),
        "lon": getattr(args, "lon", None) or plot_config.get("lon"),
        "time": args.time or plot_config.get("time"),
        "time_index": args.time_index or plot_config.get("time_index", 0),
#        "datafile": getattr(args, "datafile", None) or plot_config.get("datafile"),
        "directory": args.directory or common_config.get("directory", "."),
        "no_browser": args.no_browser or common_config.get("no_browser", False),
    }

    return params


def _generate_plot(**params):
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
    """
    
    plot_type = params.get("plot_type", "scalar_wind")

    if plot_type == "scalar_wind":
        required = ["parameter", "level", "u", "v"]
        missing = [k for k in required if k not in params or params[k] is None]
        if missing:
            raise ValueError(f"For scalar_wind plots, missing: {', '.join(missing)}")

        html_path = core.write_scalar_with_wind_html(
            scalar=params["parameter"],
            u=params["u"],
            v=params["v"],
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
