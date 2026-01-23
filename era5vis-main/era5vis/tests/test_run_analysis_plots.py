'''
Tests for the run_analysis_plots function in era5vis.analysis_plots.

Author: Leah Herrfurth
Updated by Lina Brückner, January 2026:
    - Adding era5vis.core.write_scalar_with_wind_html and era5vis.core.write_skewT instead of era5vis.core.write_html
'''
from unittest.mock import patch
import pytest
from era5vis.analysis_plots import run_analysis_plots
from era5vis import cfg

@pytest.fixture
def tmp_nc_file(tmp_path):
    """
    Provide a temporary NetCDF file to simulate ERA5 data input.
    """
    f = tmp_path / "test.nc"
    f.touch()
    return f

def test_run_modellevel_sets_cfg_datafile(tmp_nc_file):
    """
    Test that run_analysis_plots correctly sets cfg.datafile and returns HTML output.
    """

     # Simulate the HTML output file that would normally be generated
    fake_html = tmp_nc_file.parent / "index.html"
    fake_html.touch()  # create an empty file

    # patch cache to return our tmp file
    with patch("era5vis.analysis_plots.Era5Cache.get_analysis_plots_data", return_value=tmp_nc_file), \
        patch("era5vis.core.write_scalar_with_wind_html", return_value=fake_html), \
        patch("era5vis.core.write_skewT_html", return_value=fake_html), \
        patch("webbrowser.get"):

        html_path = run_analysis_plots(
            parameter="t",
            level=850,
            time="2025030200",
            download_data=True,
            no_browser=True
        )

        # Verify that cfg.datafile points to our temporary NetCDF file
        assert cfg.datafile == tmp_nc_file

         # Verify that the returned HTML file exists
        assert html_path.exists()

def test_run_analysis_plots_raises_on_missing_parameter():
    """Test that missing parameter raises ValueError."""
    with pytest.raises(ValueError, match="For scalar_wind, 'parameter' and 'level' are required."):
        run_analysis_plots(parameter=None, level=850)


def test_run_analysis_plots_raises_on_missing_level():
    """Test that missing level raises ValueError."""
    with pytest.raises(ValueError, match="For scalar_wind, 'parameter' and 'level' are required."):
        run_analysis_plots(parameter="t", level=None)


def test_run_analysis_plots_vert_cross_success(tmp_nc_file):
    """Test that vert_cross plot type triggers core.write_vert_cross_html."""
    fake_html = tmp_nc_file.parent / "vert_cross.html"
    fake_html.touch()

    with patch(
        "era5vis.analysis_plots.Era5Cache.get_analysis_plots_data",
        return_value=tmp_nc_file,
    ), patch(
        "era5vis.core.write_vert_cross_html",
        return_value=fake_html,
    ) as mock_vert, patch("webbrowser.get"):

        html_path = run_analysis_plots(
            plot_type="vert_cross",
            parameter="z",
            lat0=45,
            lon0=-10,
            lat1=55,
            lon1=10,
            time="2025030200",
            download_data=True,
            no_browser=True,
        )

        assert mock_vert.called
        assert html_path.exists()
        assert html_path.name == "vert_cross.html"


def test_run_analysis_plots_vert_cross_missing_coords():
    """Test that missing coordinates raise ValueError."""
    with pytest.raises(ValueError, match="lat0, lon0, lat1, and lon1 are required"):
        run_analysis_plots(
            plot_type="vert_cross",
            parameter="z",
            lat0=45,
            lon0=0,
        )

