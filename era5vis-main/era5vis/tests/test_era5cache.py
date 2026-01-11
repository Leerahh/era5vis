import pytest
from pathlib import Path
from unittest.mock import patch
from era5vis.data_access.era5_cache import Era5Cache, request_hash

@pytest.fixture
def tmp_cache_dir(tmp_path):
    return tmp_path

def test_cached_file_is_reused(tmp_cache_dir):
    cache = Era5Cache(cache_dir=tmp_cache_dir)

    # build fake request dict to compute expected cache filename
    request_dict = {
        "product_type": ["reanalysis"],
        "variable": ["t"],
        "year": ["2025"],
        "month": ["03"],
        "day": ["02"],
        "time": ["00:00"],
        "pressure_level": ["850"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [70, -20, -30, 50],
    }

    key = request_hash(request_dict)
    fake_file = tmp_cache_dir / f"era5_{key}.nc"
    fake_file.touch()  # create cached file

    cache = Era5Cache(cache_dir=tmp_cache_dir)

    # patch download to make sure it's not called
    with patch("era5vis.data_access.era5_cache.download_era5_data") as mock_dl:
        result = cache.get_modellevel_data("t", 850, time="2025030200")
        assert result.exists()
        mock_dl.assert_not_called()

def test_download_called_when_cache_missing(tmp_cache_dir):
    cache = Era5Cache(cache_dir=tmp_cache_dir)

    def fake_download(req_dict, target):
        # simulate downloader writing a file
        target.touch()

    with patch("era5vis.data_access.era5_cache.download_era5_data", side_effect=fake_download):
        result = cache.get_modellevel_data("t", 850, time="2025030200")
        assert result.exists()
        assert result.suffix == ".nc"
