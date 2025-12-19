"""
Command line tools for ERA5vis.

Manuela Lehner
November 2025

Edited by Leah Herrfurth December 2025:
    - Using argparse instead of sys.args
    - Adding config-based plotting
"""

import sys
import webbrowser
import argparse
import yaml
import era5vis




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
        "--no-browser",
        action="store_true",
        help=(
            "Do not open a browser with the newly generated visualization, "
            "just print the path to the HTML file instead"
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
    plot_config = config.get("plot", {}) if config else {}

    return {
        "parameter": args.parameter or plot_config.get("parameter"),
        "level": args.level or plot_config.get("level"),
        "time": args.time or plot_config.get("time"),
        "time_index": args.time_index or plot_config.get("time_ind", 0),
        "no_browser": args.no_browser or plot_config.get("no_browser", False),
    }


def _generate_plot(parameter, level, time=None, time_index=0, no_browser=False):
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
    no_browser : bool, optional
        If True, do not open the browser, by default False
    """
    if parameter is None or level is None:
        parser = argparse.ArgumentParser()
        parser.error(
            "era5vis_modellevel: command not understood. "
            "Parameter and level are required. "
            "Type 'era5vis_modellevel --help' for usage information."
        )
    else:
        html_path = era5vis.write_html(
            parameter,
            level=level,
            time=time,
            time_ind=time_index,
        )

        if no_browser:
            print("File successfully generated at:", html_path)
        else:
            webbrowser.get().open_new_tab(f"file://{html_path}")
