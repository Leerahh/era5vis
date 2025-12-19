"""
Fixtures used in ERA5vis tests.

Edited by Leah Herrfurth December 2025:
    - Added fixtures to create incomplete config files and combine CLI/config test cases
"""

from datetime import datetime

import pytest
import xarray as xr
import yaml

from era5vis import cfg


@pytest.fixture
def retrieve_param_level_from_ds():

    # retrieve variable name and level from the dataset to make sure 
    # that we don't call the function with bad arguments
    with xr.open_dataset(cfg.datafile) as ds:
        param = [variable for variable in ds.variables if
                 ("pressure_level" in ds[variable].dims) and ("longitude" in ds[variable].dims)][0]
        level = ds.pressure_level.to_numpy()[0].astype(int)

    return param, level


@pytest.fixture
def retrieve_param_level_time_from_ds():

    # retrieve variable name, level, and time from the dataset to make sure 
    # that we don't call the function with bad arguments
    with xr.open_dataset(cfg.datafile) as ds:
        param = [variable for variable in ds.variables if
                 ("pressure_level" in ds[variable].dims) and ("longitude" in ds[variable].dims)][0]
        level = ds.pressure_level.to_numpy()[0].astype(int)
        time = ds.valid_time.to_numpy()[0].astype(
               "datetime64[ms]").astype(datetime).strftime("%Y%m%d%H%M")

    return param, level, time


@pytest.fixture
def temp_incomplete_config_files(tmp_path, retrieve_param_level_time_from_ds):
    """
    Create temporary YAML configuration files missing either 'parameter' or 'level'.

    Returns
    -------
    list[Path]
        List of paths to the temporary config files.
    """
    param, level, time = retrieve_param_level_time_from_ds
    configs = []

    # Config 1: no parameter
    config1 = tmp_path / "config1.yaml"
    data1 = {
        "plot": {
            "level": float(level),
            "time": str(time),
            "time_index": 0,
            "no_browser": True,
        }
    }
    with open(config1, "w") as f:
        yaml.safe_dump(data1, f)
    configs.append(config1)

    # Config 2: no level
    config2 = tmp_path / "config2.yaml"
    data2 = {
        "plot": {
            "parameter": str(param),
            "time": str(time),
            "time_index": 0,
            "no_browser": True,
        }
    }
    with open(config2, "w") as f:
        yaml.safe_dump(data2, f)
    configs.append(config2)

    return configs


@pytest.fixture
def incomplete_test_cases(retrieve_param_level_time_from_ds, temp_incomplete_config_files):
    """
    Combine CLI-only and config-only test cases for missing arguments.

    Returns
    -------
    list[list[str]]
        List of argument lists representing incomplete test cases.
    """
    return make_incomplete_test_cases(retrieve_param_level_time_from_ds, temp_incomplete_config_files)


def make_incomplete_test_cases(retrieve_param_level_time_from_ds, temp_config_files):
    """
    Helper function to generate incomplete test cases.

    Parameters
    ----------
    retrieve_param_level_time_from_ds : tuple
        (parameter, level, time)
    temp_config_files : list[Path]
        List of paths to incomplete YAML configuration files.

    Returns
    -------
    list[list[str]]
        List of argument lists for CLI tests.
    """
    param, level, _ = retrieve_param_level_time_from_ds
    cases = []

    # CLI-only incomplete cases
    cases.append(["-p", str(param), "--no-browser"])
    cases.append(["-lvl", str(level), "--no-browser"])

    # Config-only incomplete cases
    for config_file in temp_config_files:
        cases.append([str(config_file)])

    return cases
