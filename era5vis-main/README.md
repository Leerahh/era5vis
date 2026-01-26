# era5vis

era5vis is a Python package providing command-line tools and a small API for visualizing ERA5 pressure-level reanalysis data in a web browser.

The package supports:

* horizontal scalar fields with wind vectors
* Skew-T diagrams for atmospheric soundings
* plotting vertical cross sections on a specific transect

It was developed as part of the Scientific Programming course at the University of Innsbruck and serves both as a functional visualization tool and as a template for student semester projects.

The package is inspired by the example projects scispack and climvis by Fabien Maussion.


## Installation

### Dependencies

The following Python packages are required:

* numpy
* pandas
* xarray
* netCDF4
* matplotlib
* cartopy
* metpy
* cdsapi
* pyyaml
* pytest


To download real ERA5 data, the additional dependency `cdsapi` is required.

### Install in development mode

From the repository root directory:
~~~
pip install -e .
~~~

## ERA5 Data Handling

By default, era5vis uses example ERA5 NetCDF files shipped with the package.
This allows the tools to run without downloading data or configuring a CDS account.

To download real ERA5 data from the Copernicus Climate Data Store:

1. Register at [https://cds.climate.copernicus.eu](https://cds.climate.copernicus.eu)
2. Configure your API key in `~/.cdsapirc`
3. Use the `--download_data` flag when running the CLI

Downloaded files are cached locally and reused automatically.


## Command Line Interface

The main command-line tool is:
~~~
era5vis_analysis_plots
~~~
To display all available options:
~~~
era5vis_analysis_plots --help
~~~
To use the provided example configuration file:
~~~
era5vis_analysis_plots config/config.yaml
~~~

This generates the default plot type: scalar_ wind. To use the configuration file for the other two plot types:
~~~
era5vis_analysis_plots config/config.yaml --pl skewT
era5vis_analysis_plots config/config.yaml --pl vert_cross
~~~


## Example Usage

### Scalar field with wind vectors
~~~
era5vis_analysis_plots
--plot_type scalar_wind
--parameter z
--level 500
--time 202510010000
~~~

### Skew-T diagram
~~~
era5vis_analysis_plots
--plot_type skewT
--lat 47.26
--lon 11.38
--time 202510010000
~~~

### Vertical cross section
~~~
era5vis_analysis_plots
--plot_type vert_cross
--parameter t
--lat0 40 --lon0 0
--lat1 60 --lon1 20
--time 202510010000
~~~

The generated HTML file can be opened in a web browser with:

start index.html (For Windows)
firefox index.html (For Linux & Windows)


## Configuration Files

Plot settings can be stored in a YAML configuration file and passed to the CLI:
~~~
era5vis_analysis_plots config.yaml
~~~

Command-line arguments always override values defined in the configuration file.

Example merging pattern
~~~
def cli_or_config(cli_val, config_val, default=None):
    if cli_val is not None:
        return cli_val
    elif config_val is not None:
        return config_val
    else:
        return default
~~~

## Data Download ##

For an automated download of the needed data:
~~~
era5vis_analysis_plots config/config.yaml --download_data
~~~
to the CLI.

Downloaded Data is cached and reused.

## Datafile
To analyse an already downloaded datafile:
~~~
era5vis_analysis_plots config/config.yaml --datafile path/to/file
~~~

## Arguments
| Parameter / Argument              | Default | Description / Notes                                                       |
| --------------------------------- | ------- | ------------------------------------------------------------------------- |
| `config`                          | –       | Path to configuration file (positional argument)                          |
| `--plot_type` / `--pl`            | –       | Type of plot. Options: `vert_cross`, `scalar_wind`, `skewT`               |
| `--parameter` / `-p`              | –       | ERA5 variable to plot (mandatory). Examples: `t`, `u`, `v`, `q`           |
| `--level` / `--lvl`               | None    | Pressure level in hPa (mandatory for specific-level plots)                |
| `--lat0`                          | –       | Start latitude for vertical cross-section (`vert_cross` only)             |
| `--lon0`                          | –       | Start longitude for vertical cross-section                                |
| `--lat1`                          | –       | End latitude for vertical cross-section                                   |
| `--lon1`                          | –       | End longitude for vertical cross-section                                  |
| `--lat` / `--latitude`            | –       | Latitude of single-point plots (`skewT`, `scalar_wind`)                   |
| `--lon` / `--longitude`           | –       | Longitude of single-point plots                                           |
| `--time` / `-t`                   | –       | Time to plot, format `"YYYY-MM-DDTHH:MM"` or `"YYYY-MM-DD HH:MM"`         |
| `--time_index` / `--ti`           | `0`     | Index within dataset if multiple times exist (ignored if `--time` is set) |
| `--u1` / `--horizontal_wind`      | `"u"`   | First horizontal wind component (zonal, east-west)                        |
| `--u2` / `--meridional_wind`      | `"v"`   | Second horizontal wind component (meridional, north-south)                |
| `--npoints`                       | `200`   | Number of interpolation points along vertical cross-section line          |
| `--directory` / `--directory DIR` | `"."`   | Directory to save HTML output                                             |
| `--no_browser` / `--no-browser`   | `False` | If set, do not open the plot automatically; just print the HTML file path |
| `--download_data` / `--dd`        | `False` | Download ERA5 data from CDS automatically if missing                      |
| `--datafile` / `--df`             | –       | Path to ERA5 data file (overrides config file setting)                    |
| `-h` / `--help`                   | –       | Show help message                                                         |
| `--v` / `--version`               | –       | Show program version number                                               |

## Arguments

The `era5vis_analysis_plots` command accepts parameters via the command line and/or a YAML configuration file.  
Command-line arguments always override configuration file values.

---

### 🔹 General arguments (all plot types)

| Argument | Default | Description |
|--------|---------|-------------|
| `config` | – | Path to YAML configuration file (positional argument) |
| `--plot_type`, `--pl` | `scalar_wind` | Plot type: `scalar_wind`, `skewT`, `vert_cross` |
| `--directory` | `.` | Directory to save HTML and PNG output |
| `--no-browser` | `False` | Do not open the plot automatically |
| `--download_data`, `--dd` | `False` | Download ERA5 data from CDS |
| `--datafile`, `--df` | – | Path to ERA5 NetCDF file (overrides config) |
| `--version`, `--v` | – | Show program version |
| `--help`, `-h` | – | Show help message |

> **Note**  
> `--download_data` and `--datafile` cannot be used together.

---

### 🔹 Time selection

| Argument | Default | Description |
|--------|---------|-------------|
| `--time`, `-t` | – | Time to plot (`YYYYmmddHHMM`) |
| `--time_index`, `--ti` | `0` | Time index if `--time` is not provided |

---

## 🟦 `scalar_wind` (default)

Horizontal scalar field with wind vectors.

### Required arguments

| Argument | Description |
|--------|-------------|
| `--parameter`, `-p` | ERA5 scalar variable (e.g. `t`, `z`) |
| `--level`, `--lvl` | Pressure level in hPa |

### Optional arguments

| Argument | Default | Description |
|--------|---------|-------------|
| `--u1`, `--horizontal_wind` | `u` | Zonal wind component |
| `--u2`, `--meridional_wind` | `v` | Meridional wind component |
| `--time`, `-t` | – | Datetime to plot |
| `--time_index`, `--ti` | `0` | Time index fallback |

---

## 🟩 `skewT`

Vertical atmospheric sounding (Skew-T diagram with hodograph).

### Required arguments

| Argument | Description |
|--------|-------------|
| `--lat`, `--latitude` | Latitude in degrees |
| `--lon`, `--longitude` | Longitude in degrees |
| `--time`, `-t` | Datetime (`YYYYmmddHHMM`) |

### Optional arguments

| Argument | Default | Description |
|--------|---------|-------------|
| `--directory` | `.` | Output directory |
| `--datafile` | – | ERA5 NetCDF file |

---

## 🟥 `vert_cross`

Vertical cross section along a transect.

### Required arguments

| Argument | Description |
|--------|-------------|
| `--parameter`, `-p` | ERA5 variable to plot |
| `--lat0` | Start latitude |
| `--lon0` | Start longitude |
| `--lat1` | End latitude |
| `--lon1` | End longitude |

### Optional arguments

| Argument | Default | Description |
|--------|---------|-------------|
| `--npoints` | `200` | Number of interpolation points along transect |
| `--u1` | `u` | Zonal wind component |
| `--u2` | `v` | Meridional wind component |
| `--time`, `-t` | – | Datetime or nearest available time |

---

### 🔁 Argument precedence

1. Command-line arguments  
2. Plot-type–specific configuration  
3. Global configuration  
4. Internal defaults







## Programmatic Usage

era5vis can also be used directly from Python:

~~~
from era5vis.analysis_plots import run_analysis_plots

run_analysis_plots(
    plot_type="scalar_wind",
    parameter="z",
    level=500,
    time="202501010000",
)
~~~

The function returns the path to the generated HTML file.


## Testing

Tests are run using pytest.

From the repository root directory:
~~~
pytest .
~~~


## License

Public domain.
Provided for educational purposes without warranty.
