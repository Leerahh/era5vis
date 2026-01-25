"""
Test functions for cli.py

Edited by Leah Herrfurth, December 2025
    - Using parametrized pytest to test the CLI functions
    - Adding config testcases  
Edited by Lina Brückner, January 2026
    - Adding parameters u and v
"""

import era5vis

import pytest
import yaml

from era5vis.cli import analysis_plots


@pytest.mark.parametrize("args", [
    [],
    ["-h"],
    ["--help"],
])
def test_help(capsys, args):
    """Test that help flags print usage information and exit."""
    # CLI exit after printing help
    with pytest.raises(SystemExit) as exc:
        analysis_plots(args)

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "usage: era5vis_analysis_plots" in captured.out


@pytest.mark.parametrize("args", [
    ["--v"],
    ["--version"],
])
def test_version(capsys, args):
    """Test that version flags print version information and exit."""
    # CLI should exit after printing version info
    with pytest.raises(SystemExit) as exc:
        analysis_plots(args)

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert era5vis.__version__ in captured.out


@pytest.mark.parametrize("extra_args", [
    ["--no-browser", "-t", "202510010000"],  # explicit time with no browser
    ["--ti", "0", "--no-browser", "-t", "202510010000"],  # time index instead of explicit time
    ["-t", "202510010000", "--no-browser", "--u1", "u", "--u2", "v"]  # explicit time and wind parameters
])
def test_print_html(capsys, extra_args, retrieve_param_level_time_wind_from_ds):
    """Test that correctly formatted CLI calls generate HTML output."""
    # retrieve valid parameter, level, time and wind components
    param, level, time, u, v = retrieve_param_level_time_wind_from_ds
    # construct CLI argument list
    args = ["-p", str(param), "--lvl", str(level), "--u1", "u", "--u2", "v"] + extra_args

    # run CLI
    analysis_plots(args)
    # capture output
    captured = capsys.readouterr()
    # verify that file was reported as generated
    assert "File successfully generated at:" in captured.out


def test_html_print_with_config(capsys, tmp_path, retrieve_param_level_time_wind_from_ds):
    """Test CLI reading from a YAML configuration file."""
    # retrieve valid parameter, level, time and wind components
    param, level, time, u, v = retrieve_param_level_time_wind_from_ds

    # create temporary YAML config file
    config_file = tmp_path / "config.yaml"
    
    # mimic CLI call
    config_data = {
        "plot_type": "scalar_wind",
        "no_browser": True,
        "directory": ".",
        "scalar_wind": {
            "parameter": "z",
            "u": "u",
            "v": "v",
            "level": 500,
            "time": "2025-10-01T00:00",
        },
    }

    # write YAML configuration to disk
    with open(config_file, "w") as f:
        yaml.safe_dump(config_data, f)

    # call CLI with only the config file path
    analysis_plots([str(config_file)])
    # capture CLI output
    captured = capsys.readouterr()
    # verify that file was reported as generated
    assert "File successfully generated at:" in captured.out


@pytest.mark.parametrize("args", [0, 1, 2, 3])
def test_error(capsys, args, incomplete_test_cases):
    """Test that incomplete config/CLI calls raise a SystemExit."""
    bad_args = incomplete_test_cases[args]

    with pytest.raises(ValueError) as exc:
        analysis_plots(bad_args)



@pytest.mark.parametrize(
    "config_index, cli_option",
    [
        (0, "-p"),  # missing parameter in config
        (1, "--lvl"),  # missing level in config
    ]
)
def test_cli_overrides_config(
    capsys,
    config_index,
    cli_option,
    temp_incomplete_config_files,
    retrieve_param_level_time_wind_from_ds,
):
    """Test that CLI arguments override YAML configuration values."""
    # retrieve valid parameter, level, time and wind components
    param, level, time, u, v = retrieve_param_level_time_wind_from_ds
    # select incomplete config file
    config_file = temp_incomplete_config_files[config_index]

    # construct CLI arguments depending on which config value is missing
    if cli_option == "-p":
        args = [
            str(config_file),
            "-p", param,  # override missing parameter
            "--lvl", str(level),
            "--u1", "u",
            "--u2", "v",
            "--no-browser",
            "-t", "202510010000"
        ]
    else:
        args = [
            str(config_file),
            "--lvl", str(level),  # override missing level
            "-p", param,
            "--u1", "u",
            "--u2", "v",
            "--no-browser",
            "-t", "202510010000"
        ]

    # run CLI with overrides
    analysis_plots(args)
    # capture output
    captured = capsys.readouterr()
    # verify that file was reported as generated
    assert "File successfully generated at:" in captured.out
