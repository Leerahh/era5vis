from pathlib import Path
from era5vis.data_access.download_era5 import download_era5_data
from era5vis.data_access.era5_request import Era5Request
from era5vis.utils.hashing import request_hash

class Era5Cache:
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path.cwd()

    def get_modellevel_data(self, parameter, level, time=None):
        request = Era5Request(
            product_type=["reanalysis"],
            variable=[parameter],
            year=[time[0:4]] if time else ["2025"],
            month=[time[4:6]] if time else ["03"],
            day=[time[6:8]] if time else ["02", "03", "04"],
            time=[f"{time[8:10]}:00"] if time else [
                f"{h:02d}:00" for h in range(24)
            ],
            pressure_level=[str(level)],
            data_format="netcdf",
            download_format="unarchived",
            area=[70, -20, -30, 50],
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
