## Overall Purpose of ERA5vis

ERA5vis is a command-line tool designed to visualize ERA5 climate data. At a high level, it:

1. Loads ERA5 data from NetCDF files
2. Selects variables, time ranges and model or pressure levels
3. Processes the data as needed
4. Creates visualizations using matplotlib
5. Displays or saves the resulting plots

The code is organized so that each step is handled by a different set of functions, following a clear separation of responsibilities.

## Main Components and Their Roles

### 1. Command-Line Interface (CLI) Function

**Location:** `era5vis/cli.py`

The function `era5vis_modellevel` is the entry point of the tool when it is called from the terminal. This function is responsible for:

* Handling user interaction via the command line
* Parsing command-line arguments
* Coordinating the execution of the underlying logic

This function does not perform data processing or plotting itself. Instead, it orchestrates the workflow by calling other functions.

### 2. Argument Parsing

Argument parsing is typically handled within the CLI module using the `argparse` library. These functions:

* Define which command-line options are available to the user
* Validate user input
* Convert string arguments into Python objects

Keeping argument parsing separate from data processing makes the code easier to maintain and extend.

### 3. Data Loading Functions

These functions are responsible for reading ERA5 data files. Their role is to:

* Open NetCDF datasets
* Load data into memory as `xarray.Dataset` or `xarray.DataArray` objects
* Return the loaded data for further processing

They focus only on input/output operations and do not perform visualization or analysis.

### 4. Data Processing Functions

Data processing functions handle the scientific logic of the tool. Typical tasks include:

* Selecting specific variables or model levels
* Subsetting data by time or pressure level
* Converting units or computing derived quantities

These functions take data as input and return processed data, making them easy to test and reuse.

### 5. Plotting and Visualization Functions

Plotting functions are responsible for creating visual output using `matplotlib`. Their tasks include:

* Generating figures from processed data
* Customizing plots (labels, color scales, etc.)
* Displaying or saving figures

Separating plotting logic from data processing makes it easier to add new visualization features.

### 6. Utility and Helper Functions

Utility functions provide small, reusable pieces of functionality, such as handling file paths or defining default settings. They help reduce code duplication and keep the main functions readable.
