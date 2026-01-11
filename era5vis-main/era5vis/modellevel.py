import webbrowser
import argparse
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
        parser = argparse.ArgumentParser()
        parser.error(
            "era5vis_modellevel: command not understood. "
            "Parameter and level are required. "
            "Type 'era5vis_modellevel --help' for usage information."
        )

    else:
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

    
        if no_browser:
            print("File successfully generated at:", html_path)
        else:
            webbrowser.get().open_new_tab(f"file://{html_path}")

    return html_path
