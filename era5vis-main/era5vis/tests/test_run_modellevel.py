from unittest.mock import patch
from pathlib import Path
import pytest
from era5vis.modellevel import run_modellevel
from era5vis import cfg

@pytest.fixture
def tmp_nc_file(tmp_path):
    f = tmp_path / "test.nc"
    f.touch()
    return f

def test_run_modellevel_sets_cfg_datafile(tmp_nc_file):
    fake_html = tmp_nc_file.parent / "index.html"
    fake_html.touch()  # <-- create an empty file

    # patch cache to return our tmp file
    with patch("era5vis.modellevel.Era5Cache.get_modellevel_data", return_value=tmp_nc_file), \
         patch("era5vis.write_html", return_value=tmp_nc_file.parent / "index.html"), \
         patch("webbrowser.get"):

        html_path = run_modellevel(
            parameter="t",
            level=850,
            time="2025030200",
            download_data=True,
            no_browser=True
        )

        assert cfg.datafile == tmp_nc_file
        assert html_path.exists()

def test_run_modellevel_raises_on_missing_parameter():
    with pytest.raises(SystemExit) as exc:
        run_modellevel(parameter=None, level=850)
    assert exc.value.code == 2

def test_run_modellevel_raises_on_missing_level():
    with pytest.raises(SystemExit) as exc:
        run_modellevel(parameter="t", level=None)
    assert exc.value.code == 2