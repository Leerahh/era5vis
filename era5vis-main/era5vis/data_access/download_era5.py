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

Author: Leah Herrfurth
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
