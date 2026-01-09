import cdsapi


def download_era5_data():
    """
    Download ERA5 data from the Copernicus Climate Data Store.

    Parameters
    ----------
    request : dict
        Dictionary containing the ERA5 data request parameters.
    target : str
        Path to save the downloaded data file.
    """
    client = cdsapi.Client()
    dataset = "reanalysis-era5-pressure-levels"
    request = {
    "product_type": ["reanalysis"],
    "variable": [
        "geopotential",
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


