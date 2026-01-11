import webbrowser
import era5vis
from era5vis.data_access.era5_cache import Era5Cache

def run_modellevel(
    parameter,
    level,
    time=None,
    time_index=0,
    download_data=False,
    no_browser=False,
):
    if parameter is None or level is None:
        raise ValueError("Parameter and level are required")

    if download_data:
        cache = Era5Cache()
        datafile = cache.get_modellevel_data(parameter, level, time)
    else:
        datafile = era5vis.cfg.example_datafile

    era5vis.cfg.set_datafile(datafile)

    html_path = era5vis.write_html(
        parameter,
        level=level,
        time=time,
        time_ind=time_index,
    )

    if not no_browser:
        webbrowser.get().open_new_tab(f"file://{html_path}")

    return html_path
