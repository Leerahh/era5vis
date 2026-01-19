"""
Updated by Lina Brückner, January 2026:
    - Implementing all pressure levels
"""
from pathlib import Path
import pandas as pd
from era5vis.data_access.download_era5 import download_era5_data
from era5vis.data_access.era5_request import Era5Request
from era5vis.utils.hashing import request_hash

ALL_PRESSURE_LEVELS = [
    "1000", "975", "950", "925", "900", "875", "850",
    "825", "800", "775", "750", "700", "650", "600",
    "550", "500", "450", "400", "350", "300",
    "250", "225", "200", "175", "150", "125", "100"
]

class Era5Cache:
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path.cwd()

    def get_analysis_plots_data(self, variables, level, time=None):
        if time is None:
            raise ValueError("time not available")

        t = pd.to_datetime(time)
        
        if level is None:
            # skewT → full vertical column
            pressure_levels = ALL_PRESSURE_LEVELS
        else:
        # scalar_wind → single level or list of levels
            if isinstance(level, (list, tuple)):
                pressure_levels = [str(lvl) for lvl in level]
            else:
                pressure_levels = [str(level)]

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
            area=[70, -20, 30, 50],
        )

        req_dict = request.to_dict()
        key = request_hash(req_dict)
        target = self.cache_dir / f"era5_{key}.nc"

        if target.exists():
            return target

        download_era5_data(req_dict, target=target)

        if not target.exists():
            raise RuntimeError(f"ERA5 download failed: {target}")

        return target
