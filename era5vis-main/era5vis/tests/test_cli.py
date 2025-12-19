""" Test functions for cli """

import era5vis
from era5vis.cli import modellevel
import pytest
from pathlib import Path
import yaml



@pytest.mark.parametrize("args", [
    [],
    ["-h"],
    ["--help"],
])
def test_help(capsys, args):
    with pytest.raises(SystemExit) as exc:
            modellevel(args)

    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert "usage: era5vis_modellevel" in captured.out

@pytest.mark.parametrize("args", [
    ["-v"],
    ["--version"],
])
def test_version(capsys,args):

    with pytest.raises(SystemExit) as exc:
        modellevel(args)

    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert era5vis.__version__ in captured.out



@pytest.mark.parametrize("extra_args", [
    ['--no-browser'],
    ['-ti', '0', '--no-browser'],
    ['-t', '202510010000', '--no-browser']
])
def test_print_html(capsys, extra_args, retrieve_param_level_time_from_ds):
    # fixture provides param and level
    param, level, time = retrieve_param_level_time_from_ds

    # build final CLI args as strings
    args = ['-p', str(param), '-lvl', str(level)] + extra_args

    # check that correctly formatted calls run successfully
    modellevel(args)
    captured = capsys.readouterr()
    assert 'File successfully generated at:' in captured.out



@pytest.mark.parametrize("args", [0, 1, 2, 3])
def test_error(capsys,args, incomplete_test_cases):
    # check that incorrectly formatted calls raise an error
    with pytest.raises(SystemExit) as exc:
        modellevel(incomplete_test_cases[args])

    assert exc.value.code == 2 
    

    captured = capsys.readouterr()
    assert "command not understood" in captured.err


def test_with_config(capsys, tmp_path, retrieve_param_level_time_from_ds):
    param, level, time = retrieve_param_level_time_from_ds

    # Create a temporary YAML file
    config_file = tmp_path / "config.yaml"

    # Example content
    config_data = {
        "plot": {
            "parameter": str(param),
            "level": float(level),
            "time": str(time),
            "time_index": 0,
            "no_browser": True
        }
    }

    # Write YAML
    with open(config_file, "w") as f:
        yaml.safe_dump(config_data, f)

    # Convert path to string and pass to CLI
    modellevel([str(config_file)])
    captured = capsys.readouterr()
    assert 'File successfully generated at:' in captured.out


@pytest.mark.parametrize(
    "config_index, cli_option",
    [
        (0, "-p"),     # first config: override parameter
        (1, "-lvl"),   # second config: override level
    ]
)
def test_cli_overrides_config(capsys, config_index, cli_option, temp_config_files, retrieve_param_level_time_from_ds):
    param, level, time = retrieve_param_level_time_from_ds

    config_file = temp_config_files[config_index]

    # Dynamically choose the value to override from the fixture
    cli_value = param if cli_option == "-p" else level
    args = [str(config_file), cli_option, str(cli_value), "--no-browser"]

    modellevel(args)

    captured = capsys.readouterr()
    assert "File successfully generated at:" in captured.out


