""" contains command line tools of ERA5vis

Manuela Lehner
November 2025
"""

import sys
import webbrowser
import argparse
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
   
    if args.parameter is None or args.level is None:
        parser.error("era5vis_modellevel: command not understood. "
              "Type 'era5vis_modellevel --help' for usage information.")
    
    else:
        html_path = era5vis.write_html(
            args.parameter,
            level=args.level,
            time=args.time,
            time_ind=args.time_index,
        )

        if args.no_browser:
            print("File successfully generated at:", html_path)
        else:
            webbrowser.get().open_new_tab('file://' + str(html_path))



def era5vis_modellevel():
    """Entry point for the era5vis_modellevel application script"""
    modellevel(sys.argv[1:])
