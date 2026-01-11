from dataclasses import dataclass

@dataclass
class Era5Request:
    """Class for keeping track of an ERA5 request."""
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