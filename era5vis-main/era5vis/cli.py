"""
Command line tools for ERA5vis.

Manuela Lehner
November 2025

Edited by Leah Herrfurth December 2025:
    - Using argparse instead of sys.args
    - Adding config-based plotting
Edited by Lina Brückner January 2026:
    - CLI entry points for scalar_wind and skewT plots
    - Add plot type as command line argument
    - Add directory to save plots
"""

import sys
import webbrowser
import argparse
import yaml
import era5vis
import os
from pathlib import Path

def generate_plot(params):
    """
    Main entry function for the CLI tool (supports scalar_wind or skewT).

    Parameters
    ----------
    params : dict
        Dictionary containing all final plotting parameters, 
        including plot_type, datafile, directory, and plot-specific args.
    """
    import os
    import webbrowser
    import era5vis

    # Ensure output directory exists
    if not params.get('directory'):
        params['directory'] = os.path.abspath(".")
    else:
        params['directory'] = os.path.abspath(params['directory'])
        os.makedirs(params['directory'], exist_ok=True)

    # Determine which plot type to generate
    plot_type = params.get('plot_type', 'scalar_wind')

    if plot_type == 'scalar_wind':
        # Required arguments for scalar_wind
        missing = [arg for arg in ['parameter', 'u', 'v', 'level', 'datafile'] if not params.get(arg)]
        if missing:
            raise ValueError(f"Missing required arguments for scalar_wind plot: {', '.join(missing)}")

        # Call the plotting function
        html_path = era5vis.write_scalar_with_wind_html(
            scalar=params['parameter'],
            u=params['u'],
            v=params['v'],
            level=params['level'],
            time=params.get('time'),
            time_index=params.get('time_index', 0),
            datafile=params['datafile'],
            directory=params['directory']
        )

    elif plot_type == 'skewT':
        # Required arguments for skewT
        missing = [arg for arg in ['lat', 'lon', 'time', 'datafile'] if not params.get(arg)]
        if missing:
            raise ValueError(f"Missing required arguments for skewT plot: {', '.join(missing)}")

        # Call the plotting function
        html_path = era5vis.write_skewT_html(
            lat=params['lat'],
            lon=params['lon'],
            time=params['time'],
            datafile=params['datafile'],
            directory=params['directory']
        )

    else:
        raise ValueError(f"Unknown plot_type '{plot_type}' specified.")

    # Handle browser opening
    if params.get('no_browser', False):
        print("File successfully generated at:", html_path)
    else:
        webbrowser.get().open_new_tab(f'file://{html_path}')

def era5vis_generate_plot():
    """Entry point for the era5vis_modellevel application script."""
    parsed_args = _parse_args(sys.argv[1:])
    config = _load_config(parsed_args.config) if parsed_args.config else {}
    params = _merge_config_and_args(parsed_args, config)
    generate_plot(params)
   
    

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
    
    parser.add_argument(
        '--plot_type',
        choices=['scalar_wind', 'skewT'],
        default=None,
        help=('Type of plot to generate (overrides config if provided)')
        )
    
    parser.add_argument(
        "--directory",
        metavar="DIR",
        help="Directory where the HTML file will be saved (overrides config)"
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

    Returns a final params dict.
    """

    # Determine plot type: CLI arg overrides config
    plot_type = args.plot_type or config.get("plot_type", "scalar_wind")

    # Get plot-type-specific section from config
    plot_config = config.get(plot_type, {})

    # Get common parameters from config
    common_config = config.get("common", {})

    # Start with common + plot-specific config
    params = {**common_config, **plot_config}

    # Override with CLI args if provided
    cli_args = vars(args)
    for k, v in cli_args.items():
        if v is not None:
            params[k] = v

    # Always store plot_type
    params["plot_type"] = plot_type

    # Make datafile absolute **relative to YAML file** if provided
    if "datafile" in params and args.config:
        yaml_dir = Path(args.config).parent
        params["datafile"] = str((yaml_dir / params["datafile"]).resolve())

    # Ensure directory exists
    if "directory" not in params or not params["directory"]:
        params["directory"] = str(Path(".").resolve())
    else:
        params["directory"] = str(Path(params["directory"]).resolve())
        os.makedirs(params["directory"], exist_ok=True)

    return params
