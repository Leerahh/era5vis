## Self-Report on Project Contribution - Lina Brückner

### What task was assigned to you at the beginning of the project?

At the start of the project, I was responsible for extending the plotting capabilities of the package. Specifically, my tasks were:

* adding wind barbs to the geopotential height plot and
* implementing a Skew-T diagram as an additional plotting option.

At that stage, responsibilities for the guided exercise and the joint functionality of the package had not yet been clearly defined.


### What changed during the implementation, and what is the outcome of the project?

I was able to implement the two new plotting functionalities relatively quickly. However, my focus soon shifted toward integrating these features into the overall package structure. This integration required substantial modifications across almost all modules, as well as corresponding updates to the test suite, which ultimately took up the majority of my time.

In the final phase of the project, I revised the documentation for each module and function, updated the `README.md` file, and checked (hopefully) the entire codebase for PEP 8 compliance. In the end, I also checked and updated each test file to ensure that all newly added functionalities were properly covered.

As a final and somewhat spontaneous improvement, I introduced a single common example data file that supports all three plot types. And in a very last step, I focused on testing all command-line input options consistently.


### What was the biggest challenge you faced during implementation?

At the beginning of the project, I struggled with using GitHub, as this was my first experience working with the platform. I was unable to set up GitHub Desktop in a timely manner and therefore decided to work locally, manually reuploading my changes to the repository. Later, as I became more familiar with GitHub, I realized that this workflow was really inefficient, as repeatedly redownloading and reinstalling the package was time-consuming and inconvenient.

From a programming perspective, the most challenging task was implementing the Skew-T plotting option within the `cli.py` module. In particular, defining all necessary command-line arguments and linking them correctly to the updated `config.yaml` file proved to be complex. This part of the implementation became somewhat chaotic, which required frequent adjustments to the test suite — especially `test_cli.py` — to keep everything consistent.


### What was the biggest challenge when merging everyone’s work into one package?

In my view, the main challenge during the group integration phase was adapting the automated data download functionality to support the newly added plotting options. Originally, this functionality had been designed exclusively for the initial geopotential height plot. As a result, I spent considerable time extending the `download_data` option in `cli.py` and aligning it with the updated `config.yaml` structure. These changes again required multiple updates to the test suite to ensure that all combinations of plotting and download options worked correctly.it had been designed only for the initial simple geopotential height plot. I therefore spent considerable time updating the download_data option in cli.py and aligning it with the config.yaml file, which again came along with many updates in the tests.
