## Self-Report on Project Contribution - Lina Brückner

### What task was assigned to you at the beginning of the project?

At the start of the project, I was responsible for extending the plotting capabilities of the package. Specifically, my tasks were:

* adding wind barbs to the geopotential height plot and
* implementing a Skew-T diagram as an additional plotting option.

At that stage, responsibilities for the guided exercise and the joint functionality of the package had not yet been clearly defined.


### What changed during the implementation and what is the outcome of the project?

I was able to implement the two new plotting functionalities relatively quickly. However, my focus soon shifted toward integrating these features into the overall package structure. This integration required substantial modifications across almost all modules, as well as corresponding updates to the test suite, which ultimately took up the majority of my time.

I also implemented several changes in the configuration file and had to experiment for a while until I found a good solution regarding what should be covered in the configuration file and what should not.

At some point, I considered extending the first plot to support scalar fields other than geopotential. However, I later decided against this approach, as I did not manage to implement the necessary data background quickly enough and eventually ran out of time.

In the final phase of the project, I revised the documentation for each module and function, updated the `README.md` file, and checked (hopefully) the entire codebase for PEP 8 compliance. In addition, I reviewed and updated each test file to ensure that all newly added functionalities were properly tested.

As a final and somewhat spontaneous improvement, I introduced a single common example data file that supports all three plot types, since we had also added the option for users to select an individual data file. In a very last step, I focused on testing all command-line input options consistently.


### What was the biggest challenge you faced during implementation?

At the beginning of the project, I struggled with using GitHub, as this was my first experience working with the platform. I was unable to set up GitHub Desktop in a timely manner and therefore decided to work locally on the package, manually re-uploading my changes to the repository. Only later, as I became more familiar with GitHub, did I realize that this workflow was highly inefficient, since repeatedly re-downloading and reinstalling the package was time-consuming and inconvenient.

From a programming perspective, the most challenging task was implementing the Skew-T plotting option within the `cli.py` module. In particular, defining all necessary command-line arguments and linking them correctly to the updated `config.yaml` file proved to be complex. This part of the implementation became somewhat chaotic due to my own mistakes, which also required frequent adjustments to the test suite — especially `test_cli.py` — to keep everything consistent.

Overall, I am convinced that I learned a lot during the project phase, ranging from programming in a more structured manner, to properly documenting code and functions, and to understanding the interconnections within the package.


### What was the biggest challenge when merging everyone’s work into one package?

In my view, the main challenge during the group integration phase was adapting the automated data download functionality to support the newly added plotting options. Originally, this functionality had been designed exclusively for the initial geopotential height plot. As a result, I spent considerable time extending the download_data option in `cli.py` and aligning it with the updated `config.yaml` structure. These changes again required multiple updates to the test suite to ensure that all combinations of plotting and download options worked correctly.

In the final phase, I changed parts of the documentation without regularly testing and without realizing that even small issues, such as incorrect indentation, could cause the entire package to fail. This resulted in many repeated attempts with errors - also for my group members-, as I initially assumed I had only made minor documentation changes.
