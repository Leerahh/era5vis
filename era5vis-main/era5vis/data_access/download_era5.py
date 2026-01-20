"""
ERA5 data download utilities.

This module provides a thin wrapper around the Copernicus Climate Data
Store (CDS) API for downloading ERA5 pressure-level data in NetCDF format.

It assumes that the user has:
- a valid CDS account
- an API key configured via ``~/.cdsapirc``

The module does not perform any validation of the request dictionary
and delegates request construction to higher-level components.

Notes
-----
Access to ERA5 data requires registration at:
https://cds.climate.copernicus.eu/
"""
import cdsapi


def download_era5_data(request, target='era5_download.nc'):
    """
    Download ERA5 pressure-level data from the Copernicus Climate Data Store.

    This function submits a data request to the CDS API and downloads
    the resulting NetCDF file to the specified target path.

    Parameters
    ----------
    request : dict
        Dictionary containing ERA5 request parameters compatible with
        the CDS API. This typically includes keys such as:
        ``product_type``, ``variable``, ``year``, ``month``, ``day``,
        ``time``, ``pressure_level``, and ``area``.
    target : str or pathlib.Path, default "era5_download.nc"
        Path where the downloaded NetCDF file will be saved.

    Notes
    -----
    - This function requires a working internet connection.
    - Authentication is handled by the CDS API via the user's
      ``~/.cdsapirc`` file.
    """

    # create a CDS API client using credentials from ~/.cdsapirc
    client = cdsapi.Client()
    # ERA5 pressure-level dataset identifier
    dataset = "reanalysis-era5-pressure-levels"
    request = request
    target = target
    # submit the request and download the data to the target file
    client.retrieve(dataset, request, target)

# ---------------------------------------------------------------------
# Example ERA5 request (for reference and testing only)
# ---------------------------------------------------------------------
#
# The following example demonstrates how a valid CDS request dictionary
# might look.
#
# To use it, copy the request dictionary and pass it to download_era5_data().
#
'''
client = cdsapi.Client()

dataset = "reanalysis-era5-pressure-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "specific_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind"
    ],
    "year": ["2025"],
    "month": ["03"],
    "day": ["02", "03", "04"],
    "time": [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ],
    "pressure_level": ["850"],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "area": [70, -20, -30, 50]
}
target = 'era5_download.nc'

client.retrieve(dataset, request, target)
'''    

