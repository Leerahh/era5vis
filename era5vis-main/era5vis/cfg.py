"""
    Configuration module containing settings and constants.
    Updated by Lina Brückner, January 2026:
        - seperate into two possible datasets
"""

from pathlib import Path


# location of data directory containing html template
pkgdir = Path(__file__).parents[0]
html_template = Path(pkgdir) / 'data' / 'template.html'

scalar_wind_datafile = Path(pkgdir) / 'data' / 'era5_example_dataset.nc'
skewT_datafile      = Path(pkgdir) / 'data' / 'era5_example_1.nc'
