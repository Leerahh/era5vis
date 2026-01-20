"""
Tests for the ERA5 cache mechanism.

Author: Leah Herrfurth

"""

import pytest
from pathlib import Path
from unittest.mock import patch
from era5vis.data_access.era5_cache import Era5Cache, request_hash

@pytest.fixture
def tmp_cache_dir(tmp_path):
    """
    Provide a temporary directory to be used as the ERA5 cache.
    """
    return tmp_path

def test_cached_file_is_reused(tmp_cache_dir):
    """
    Ensure that an existing cached ERA5 file is reused.
    """
   
    cache = Era5Cache(cache_dir=tmp_cache_dir)

    # build fake request dict to compute expected cache filename
    request_dict = {
        "product_type": ["reanalysis"],
        "variable": "t",
        "year": ["2025"],
        "month": ["03"],
        "day": ["02"],
        "time": ["00:00"],
        "pressure_level": ["850"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [70, -20, 30, 50],
    }
    # Compute the cache key and create a fake cached NetCDF file
    key = request_hash(request_dict)
    fake_file = tmp_cache_dir / f"era5_{key}.nc"
    fake_file.touch()  # create cached file

    cache = Era5Cache(cache_dir=tmp_cache_dir)

    # patch download to make sure it is not called
    with patch("era5vis.data_access.era5_cache.download_era5_data") as mock_dl:
        result = cache.get_analysis_plots_data("t", 850, time="2025-03-02T00:00")
         # The returned file should exist and come from the cache
        assert result.exists()
         # Download must not be triggered when cache is present
        mock_dl.assert_not_called()

def test_download_called_when_cache_missing(tmp_cache_dir):
    """
    Ensure that the download function is called when the cache is missing.
    """
    cache = Era5Cache(cache_dir=tmp_cache_dir)

    def fake_download(req_dict, target):
        # simulate downloader writing a file
        target.touch()
        
     # Patch the download function to simulate successful data retrieval
    with patch("era5vis.data_access.era5_cache.download_era5_data", side_effect=fake_download):
        result = cache.get_analysis_plots_data("t", 850, time="2025-12-01T00:00")
        assert result.exists()
        assert result.suffix == ".nc"
