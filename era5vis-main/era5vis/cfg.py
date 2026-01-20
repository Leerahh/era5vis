"""
Global configuration and shared paths for the era5vis package.

This module defines package-wide constants and configuration variables
used by multiple submodules, including:

- paths to HTML templates
- default and example ERA5 data files
- a global reference to the currently active ERA5 dataset

The configuration is intentionally lightweight and primarily serves
as a central place for shared paths and state.

Updated by Lina Brückner, January 2026:
    - Separated configuration into multiple dataset options
"""

from pathlib import Path

# ---------------------------------------------------------------------
# Package paths
# ---------------------------------------------------------------------

# root directory of the era5vis package
pkgdir = Path(__file__).parents[0]
# path to the HTML template
html_template = Path(pkgdir) / 'data' / 'template.html'

# ---------------------------------------------------------------------
# ERA5 data file configuration
# ---------------------------------------------------------------------

# global reference to the currently active ERA5 data file
datafile : Path | None = None
# example ERA5 datasets shipped with the package
example_datafile = Path(pkgdir) / 'data' / 'era5_example_dataset.nc'
# default path where downloaded ERA5 data are stored
downloaded_datafile = Path.cwd() / 'era5_download.nc'
# plot type specific example datasets
scalar_wind_datafile = Path(pkgdir) / 'data' / 'era5_example_dataset.nc'
skewT_datafile      = Path(pkgdir) / 'data' / 'era5_example_1.nc'

def set_datafile(path: Path):
    """
    Set the active ERA5 data file used by the era5vis package.

    This function updates the global ``datafile`` variable, which is
    accessed by plotting and analysis routines to determine which
    ERA5 dataset should be used.

    Parameters
    ----------
    path : pathlib.Path
        Path to the ERA5 NetCDF data file.

    """
    
    global datafile
    datafile = path
