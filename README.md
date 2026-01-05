# era5vis
Term Project for Scientific Programming: The ERA5vis package

## The ERA5vis package
I have put together a small package called ERA5vis. Its structure is based on the template package and the ClimVis package written by Fabien Maussion. Download the zipped package from here and extract it. Read the README and the package requirements first.
- Install the package in development mode: pip install -e . $\checkmark$
- Try the command line interface (era5vis_modellevel -h) from a terminal. $\checkmark$
- Explore setup.py:
  -- Can you find the line that makes the command available from the terminal?
    entry_points={
        'console_scripts': [
            'era5vis_modellevel=era5vis.cli:era5vis_modellevel'
        ,]
  ,},
  -- Where is the code that is being executed when you call era5vis_modellevel?
    era5vis/cli.py
- Familiarize yourself with the tool. Can you understand what the role of each function is?
- Can you run the tests successfully? Probably not. Somewhere in cfg.py, a hard-coded path is pointing to a directory that does not exist on your system.
- era5vis_modellevel -p z -lvl 500 should work fine and display a page in your browser.

## Guided exercise: make the package more robust
- The package currently contains no check whether the user-specified variable, model level, time stamp actually exist in the data file. A function definition line has alrady been created in era5.py (function check_data_availability) and a call to this function has already been added to function core.write_html. Write the function code to check if variable, model level, and time stamp are in the data file and if not raise an exception.
- Add a check to the code to make sure that the data file specified in cfg.py actually exists. If the data file does not exist, print the following message and exit the program:
- The specified data file does not exist. Please set a valid path in cfg.py.

## Project: make the package better
Now you should be ready to contribute to the package! As a group, add at least N+1 simple functionalities to it, where N is your group size. This functionality can be anything you want, as long as it makes you write some code.

Contributions:
- Leah: config-based run?
- Lina: Skew-T map
- Ilias:
- joint: merge plots to single one/automatically download data
