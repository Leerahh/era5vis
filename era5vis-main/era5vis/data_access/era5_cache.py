"""
ERA5 data caching and retrieval utilities.

This module provides a caching layer for ERA5 data requests.
It ensures that identical ERA5 requests are downloaded only once and
reused across multiple plotting operations.

The cache is based on hashing the full ERA5 request dictionary and
storing the resulting NetCDF file in a local cache directory.

Updated by Lina Brückner, January 2026:
    - Implemented support for retrieving all pressure levels
"""

from pathlib import Path
import pandas as pd
from era5vis.data_access.download_era5 import download_era5_data
from era5vis.data_access.era5_request import Era5Request
from era5vis.utils.hashing import request_hash

# complete list of ERA5 pressure levels used for vertical profiles
ALL_PRESSURE_LEVELS = [
    "1000", "975", "950", "925", "900", "875", "850",
    "825", "800", "775", "750", "700", "650", "600",
    "550", "500", "450", "400", "350", "300",
    "250", "225", "200", "175", "150", "125", "100"
]

class Era5Cache:
    """
    Local cache manager for ERA5 NetCDF data files.

    The cache stores ERA5 downloads on disk using a hash derived from
    the full request dictionary. Identical requests will always map
    to the same cached file.

    Parameters
    ----------
    cache_dir : pathlib.Path, optional
        Directory where cached ERA5 NetCDF files are stored.
        Defaults to the current working directory.
    """
    
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path.cwd()

    def get_analysis_plots_data(self, variables, level, time=None):
        """
        Retrieve ERA5 data required for analysis plots, using caching.

        This method constructs an ERA5 request based on the requested
        variables, pressure levels, and time. If an identical request
        has already been downloaded, the cached file is reused.
        Otherwise, the data are downloaded from the CDS API.

        Parameters
        ----------
        variables : list of str
            ERA5 variable names to retrieve (e.g. ``["t", "u", "v"]``).
        level : int, list of int, or None
            Pressure level(s) in hPa.
            - If None, all pressure levels are retrieved (used for Skew-T).
            - If an int, a single pressure level is retrieved.
            - If a list or tuple, multiple pressure levels are retrieved.
        time : str
            Datetime string compatible with ERA5 ``valid_time``
            (format: ``YYYYmmddHHMM``).

        Returns
        -------
        pathlib.Path
            Path to the cached or newly downloaded ERA5 NetCDF file.

        Raises
        -------
        ValueError
            If ``time`` is not provided.
        RuntimeError
            If the ERA5 download fails.
        """

        # a time specification is mandatory for ERA5 request
        if time is None:
            raise ValueError("time not available")

        # parse the time string into a pandas timestamo
        t = pd.to_datetime(time)

        # determine pressure levels based on plot type
        if level is None:
            # skew-T plots require the full vertical column
            pressure_levels = ALL_PRESSURE_LEVELS
        else:
        # scalar plots may request a single level or multiple levels
            if isinstance(level, (list, tuple)):
                pressure_levels = [str(lvl) for lvl in level]
            else:
                pressure_levels = [str(level)]

        # construct ERA5 request
        request = Era5Request(
            product_type=["reanalysis"],
            variable=variables,
            year=[f"{t.year:04d}"],
            month=[f"{t.month:02d}"],
            day=[f"{t.day:02d}"],
            time=[f"{t.hour:02d}:00"],
            pressure_level=pressure_levels,
            data_format="netcdf",
            download_format="unarchived",
            area=[70, -20, 30, 50], # North, West, South, East
        )

        # convert request object to a dictionary compatible with the CDS API
        req_dict = request.to_dict()
        # generate a unique hash for the request
        key = request_hash(req_dict)
        # define target file path in the cache directory
        target = self.cache_dir / f"era5_{key}.nc"

        # if the file already exists, reuse it
        if target.exists():
            return target

        # otherwise, download the data
        download_era5_data(req_dict, target=target)

        # verify that the download was successful
        if not target.exists():
            raise RuntimeError(f"ERA5 download failed: {target}")

        return target
