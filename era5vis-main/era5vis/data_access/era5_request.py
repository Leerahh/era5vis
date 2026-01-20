"""
ERA5 request definition.

This module defines a container class for ERA5 data requests.
The class encapsulates all parameters required by the Copernicus Climate
Data Store (CDS) API and provides a method to convert the request into
a dictionary compatible with the API.

The request object is primarily used by the ERA5 caching layer to ensure
that requests are hashable, reproducible, and easily serializable.
"""

from dataclasses import dataclass

@dataclass
class Era5Request:
    """
    Container class representing a single ERA5 data request.

    This class stores all parameters required to request ERA5
    pressure-level data from the Copernicus Climate Data Store.
    It does not perform any validation of the parameters and assumes
    that inputs conform to CDS API specifications.

    Attributes
    ----------
    product_type : list of str
        Type of ERA5 product (typically ``["reanalysis"]``).
    variable : list of str
        ERA5 variable names to retrieve (e.g. ``["t", "u", "v"]``).
    year : list of str
        Year(s) of the requested data (four-digit format).
    month : list of str
        Month(s) of the requested data (two-digit format).
    day : list of str
        Day(s) of the requested data (two-digit format).
    time : list of str
        Time(s) of the requested data (HH:MM format).
    pressure_level : list of str
        Pressure level(s) in hPa.
    data_format : str
        Output data format (e.g. ``"netcdf"``).
    download_format : str
        Download format (e.g. ``"unarchived"``).
    area : list of int
        Spatial subset defined as
        ``[north, west, south, east]`` in degrees.
    """

    product_type: [str]
    variable: [str]
    year: [str]
    month: [str]
    day: [str]
    time: [str]
    pressure_level: [str]
    data_format: str
    download_format: str
    area: [int]

    def __init__(self, product_type: str, variable: str, year: str, month: str, day: str, time: str, pressure_level: str, data_format: str, download_format: str, area: list):
        """
        Initialize an ERA5 request object.

        Parameters
        ----------
        product_type : list of str
            Type of ERA5 product (e.g. ``["reanalysis"]``).
        variable : list of str
            ERA5 variables to retrieve.
        year : list of str
            Year(s) in four-digit format.
        month : list of str
            Month(s) in two-digit format.
        day : list of str
            Day(s) in two-digit format.
        time : list of str
            Time(s) in HH:MM format.
        pressure_level : list of str
            Pressure level(s) in hPa.
        data_format : str
            Output data format (e.g. ``"netcdf"``).
        download_format : str
            Download format (e.g. ``"unarchived"``).
        area : list of int
            Spatial subset defined as
            ``[north, west, south, east]``.
        """

        # store all request parameters without modification
        self.product_type = product_type
        self.variable = variable
        self.year = year
        self.month = month
        self.day = day
        self.time = time
        self.pressure_level = pressure_level
        self.data_format = data_format
        self.download_format = download_format
        self.area = area
    
    def to_dict(self):
        """
        Convert the ERA5 request to a CDS API–compatible dictionary.

        Returns
        -------
        dict
            Dictionary representation of the ERA5 request, suitable
            for passing directly to ``cdsapi.Client.retrieve``.
        """
        return {
            "product_type": self.product_type,
            "variable": self.variable,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "time": self.time,
            "pressure_level": self.pressure_level,
            "data_format": self.data_format,
            "download_format": self.download_format,
            "area": self.area
        }
