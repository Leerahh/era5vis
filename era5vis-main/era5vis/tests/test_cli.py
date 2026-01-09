""" Test functions for cli 
Edited by Leah Herrfurth, December 2025
    - Using parametrized pytest to test the CLI functions
    - Adding config testcases  
Edited by Lina Brückner, January 2026
    - parameter u and v added
"""
import pytest
import yaml
import era5vis
from era5vis.cli import modellevel



@pytest.mark.parametrize("args", [
    [],
    ["-h"],
    ["--help"],
])
def test_help(capsys, args):
    """Test that help flags print usage information and exit."""
    with pytest.raises(SystemExit) as exc:
        modellevel(args)

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "usage: era5vis_modellevel" in captured.out


@pytest.mark.parametrize("args", [
    ["-v"],
    ["--version"],
])
def test_version(capsys, args):
    """Test that version flags print version information and exit."""
    with pytest.raises(SystemExit) as exc:
        modellevel(args)

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert era5vis.__version__ in captured.out


@pytest.mark.parametrize("extra_args", [
    #["--no-browser"],
    ["--no-browser", "-t", "202510010000"],
    ["-ti", "0", "--no-browser", "-t", "202510010000"],
    #["-ti", "0", "--no-browser"],
    #["-t", "202510010000", "--no-browser"],
    ["-t", "202510010000", "--no-browser", "-u1", "u", "-u2", "v"]
])
def test_print_html(capsys, extra_args, retrieve_param_level_time_wind_from_ds):
    """Test that correctly formatted CLI calls generate HTML output."""
    param, level, time, u, v = retrieve_param_level_time_wind_from_ds
    args = ["-p", str(param), "-lvl", str(level), "-u1", "u", "-u2", "v"] + extra_args

    modellevel(args)
    captured = capsys.readouterr()
    assert "File successfully generated at:" in captured.out


def test_html_print_with_config(capsys, tmp_path, retrieve_param_level_time_wind_from_ds):
    """Test CLI reading from a YAML configuration file."""
    param, level, time, u, v = retrieve_param_level_time_wind_from_ds

    config_file = tmp_path / "config.yaml"
    config_data = {
        "plot_type": "scalar_wind",
        "scalar_wind": {
            "parameter": "z",
            "u": "u",
            "v": "v",
            "level": 500,
            "time": "2025-10-01T00:00",
        },
        "common": {
            "no_browser": True,
            "directory": ".",
        },
    }

    with open(config_file, "w") as f:
        yaml.safe_dump(config_data, f)

    modellevel([str(config_file)])
    captured = capsys.readouterr()
    assert "File successfully generated at:" in captured.out


@pytest.mark.parametrize("args", [0, 1, 2, 3])
def test_error(capsys, args, incomplete_test_cases):
    """Test that incomplete config/CLI calls raise a ValueError."""
    with pytest.raises(ValueError) as exc:
        modellevel(incomplete_test_cases[args])
        
    assert "missing" in str(exc.value)

#    assert exc.value.code == 2
#    captured = capsys.readouterr()
#    assert "command not understood" in captured.err

@pytest.mark.parametrize(
    "config_index, cli_option",
    [
        (0, "-p"),   # first config: override parameter
        (1, "-lvl"), # second config: override level
    ]
)
def test_cli_overrides_config(capsys, config_index, cli_option, temp_incomplete_config_files, retrieve_param_level_time_wind_from_ds):
    """Test that CLI arguments override YAML configuration values."""
    param, level, time, u, v = retrieve_param_level_time_wind_from_ds
    config_file = temp_incomplete_config_files[config_index]

#   cli_value = param if cli_option == "-p" else level
#   args = [str(config_file), cli_option, str(cli_value), "-u1", "u", "-u2", "v","--no-browser"]
    if cli_option == "-p":
    # -p override, need to pass missing level
        args = [
            str(config_file),
            "-p", param,
            "-lvl", str(level),
            "-u1", "u",
            "-u2", "v",
            "--no-browser",
            "-t", "202510010000"  # provide valid time
        ]
    else:
        # -lvl override, need to pass missing parameter
        args = [
            str(config_file),
            "-lvl", str(level),
            "-p", param,
            "-u1", "u",
            "-u2", "v",
            "--no-browser",
            "-t", "202510010000"  # provide valid time
        ]

    modellevel(args)
    captured = capsys.readouterr()
    assert "File successfully generated at:" in captured.out
