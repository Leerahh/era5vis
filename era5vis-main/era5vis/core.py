"""Plenty of useful functions doing useful things.  """

from pathlib import Path
from tempfile import mkdtemp
import shutil

from era5vis import cfg, graphics, era5


def mkdir(path, reset=False):
    '''Check if directory exists and if not, create one.
        
    Parameters
    ----------
    path: str
        path to directory
    reset: bool 
        erase the content of the directory if it exists

    Returns
    -------
    path: str
        path to directory
    '''
    
    if reset and Path.is_dir(path):
        shutil.rmtree(path)
    try:
        Path.mkdir(path, parents=True)
    except FileExistsError:
        pass
    return path


def write_scalar_with_wind_html(
    scalar, u, v, level, time=None, time_index=None, directory=None, step=9, datafile=None
):
    '''
    Create HTML for scalar field with wind vectors.
    '''
    if time is None:
        time = time_index
        
    if datafile is None:
        datafile = cfg.scalar_wind_datafile
        
    # check that dataset actually contains the selected variable, time, ...
    era5.check_file_availability(datafile)
    for var in (scalar, u, v):
        era5.check_data_availability(var, level=level, time=time, datafile=datafile)

    # create a temporary directory for the plot
    if directory is None:
        directory = mkdtemp()
    mkdir(directory)

    print('Extracting data')
    da = era5.horiz_cross_section(scalar, level, time, datafile)
    u_da = era5.horiz_cross_section(u, level, time, datafile)
    v_da = era5.horiz_cross_section(v, level, time, datafile)

    print('Plotting data')

    time_safe = str(time).replace(':', '-').replace(' ', '_')
    png = Path(directory) / f'scalar_wind_{scalar}_{level}_{time_safe}.png'

    graphics.plot_scalar_with_wind(
        da, u_da, v_da, savepath=png, step=step
    )

    # create HTML from template
    outpath = Path(directory) / 'index.html'
    with open(cfg.html_template) as infile:
        template = infile.read()

    html = (
        template
        .replace('[PLOTTYPE]', 'Scalar field with wind')
        .replace('[PLOTVAR]', scalar)
        .replace('[IMGTYPE]', png.name)
    )

    with open(outpath, 'w') as infile:
        infile.write(html)

    return outpath

def write_skewT_html(
    lat, lon, time, datafile=None, directory=None, **kwargs
):
    '''
    Create HTML for a Skew-T diagram.
    '''

    if datafile is None:
        datafile = cfg.skewT_datafile

    if directory is None:
        directory = mkdtemp()
    mkdir(directory)

    print('Plotting Skew-T')
    
    time_safe = str(time).replace(':', '-').replace(' ', '_')
    png = Path(directory) / f'SkewT_{lat:.2f}_{lon:.2f}_{time_safe}.png'

    graphics.plot_skewT(
        lat=lat,
        lon=lon,
        time=time,
        datafile=datafile,
        savepath=png,
        **kwargs
    )

    outpath = Path(directory) / 'index.html'

    with open(cfg.html_template, 'r') as infile:
        lines = infile.readlines()

    out = []
    for txt in lines:
        txt = txt.replace('[PLOTTYPE]', 'Skew-T diagram')
        txt = txt.replace('[PLOTVAR]', f'{lat:.2f}°, {lon:.2f}° @ {time}')
        txt = txt.replace('[IMGTYPE]', png.name)
        out.append(txt)

    with open(outpath, 'w') as outfile:
        outfile.writelines(out)

    return outpath
