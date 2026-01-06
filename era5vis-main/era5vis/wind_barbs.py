"""contains additional wind barb plotting functions"""

from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt


def plot_horiz_wind_barbs(u, v, filepath=None, step=5):
    '''plot horizontal wind barbs from u and v wind components.

    Parameters
    ----------
    u : xarray.DataArray
        zonal wind component
    v : xarray.DataArray
        meridional wind component
    filepath : str, optional
        plot is saved to filepath if provided
    step : int, optional
        subsampling step for wind barbs (default is 5)
    '''

    # set up a single set of axes
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_position([0.1, 0.1, 0.7, 0.85])
    ax.set_xlabel(r'Longitude ($^{\circ}$)')
    ax.set_ylabel(r'Latitude ($^{\circ}$)')

    # extract time information
    time = u.valid_time.to_numpy().astype('datetime64[ms]').astype(datetime)

    # title
    ax.set_title(
        f'Wind barbs at {u.pressure_level.to_numpy()} '
        f'{u.pressure_level.units} ({time:%d %b %Y %H:%M})',
        fontsize=12
    )

    # create 2D lon/lat grid
    lon2d, lat2d = np.meshgrid(u.longitude, u.latitude)

    # plot wind barbs (subsampled)
    ax.barbs(
        lon2d[::step, ::step],
        lat2d[::step, ::step],
        u.values[::step, ::step],
        v.values[::step, ::step],
        length=6,
        pivot='middle'
    )

    if filepath is not None:
        fig.savefig(filepath)
        plt.close()

    return fig
