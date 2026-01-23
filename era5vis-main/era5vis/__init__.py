""" Updated by Lina Brückner, January 2026:
    - import write_scalar_with_wind_html and write_skewT_html instead of write_html
"""

# This is a hard coded version string.
# Real packages use more sophisticated methods to make sure that this
# string is synchronised with `setup.py`, but for our purposes this is OK
__version__ = '0.0.1'

from era5vis.core import write_scalar_with_wind_html, write_skewT_html, write_vert_cross_html
