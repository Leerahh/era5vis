""" contains command line tools of ERA5vis

Manuela Lehner
November 2025

Edited by Leah Herrfurth December 2025:
    - using argparse instead of sys.args
    - adding config-based plotting
"""

import sys
import webbrowser
import argparse

import yaml
import era5vis



def modellevel(args):
    """The actual era5vis_modellevel command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
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
            'era5vis_modellevel is provided "as is", without warranty of any kind'
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
        help=("Time index within dataset to plot (--time takes "
              "precedence if both --time and --time_index are specified) "
              "(default=0)"
              )

    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help=(
            "Do not open a browser with the newly generated visualisation, "
            "just print the path to the html file instead"
        )
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    config = {}
    if args.config:
        if not args.config.endswith((".yaml", ".yml")):
            parser.error("config must be a .yaml or .yml file")

        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    
    # Merge config values into args if CLI args are not provided
    parameter = args.parameter or config.get("plot", {}).get("parameter")
    level = args.level or config.get("plot", {}).get("level")
    time = args.time or config.get("plot", {}).get("time")
    time_index = args.time_index or config.get("plot", {}).get("time_ind", 0)
    no_browser = args.no_browser or config.get("plot", {}).get("no-browser", False)

        
   
    if parameter is None or level is None:
        parser.error("era5vis_modellevel: command not understood. "
              "Type 'era5vis_modellevel --help' for usage information.")
    
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
            webbrowser.get().open_new_tab('file://' + str(html_path))



def era5vis_modellevel():
    """Entry point for the era5vis_modellevel application script"""
    modellevel(sys.argv[1:])
