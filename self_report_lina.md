## What task was assigned to you when you started?
At the start of the project, I was responsible for:
- adding wind barbs to the geopotential height plot
- adding a Skew-T diagram as a second plotting option.
At that point, responsibilities for the guided exercise and the joint functionality had not yet been defined.

## What changed during the implementation, that is, what is the outcome of the project?
I was able to implement my main ideas—the two new functionalities for the project—relatively quickly. However, my main focus then shifted to integrating these functionalities into the overall package structure. This required extensive modifications across almost all modules of the package, as well as updates to the corresponding tests, and therefore took the majority of my time.
In the final stage, I focused on thoroughly testing all command-line input options. In addition, I updated the documentation for each module and function and rewrote the README.md file.

## What was the biggest challenge you faced in the implementation?
At the beginning, I encountered difficulties becoming familiar with GitHub, as this was my first time working with the platform. I was not able to set up GitHub Desktop in a timely manner and therefore decided to work locally on my computer, manually reuploading my changes to the package. Later on, I became more comfortable with GitHub and realized that this approach was inefficient, as repeatedly redownloading and reinstalling the package became obviously annoying.
From a programming perspective, the biggest challenge was implementing the Skew-T plotting option within the cli.py module. In particular, defining all necessary parser arguments and linking the new options to the updated config.yaml file proved to be complex. This part of the implementation became somewhat chaotic, which resulted in spending a significant amount of time on also keeping the tests up to date, especially test_cli.py.

## What was the biggest challenge when merging everyone’s work into one package?
From my point of view, the biggest challenge during the group integration phase was adapting the automated data download functionality to the new plotting functionalities. Originally, it had been designed only for the initial simple geopotential height plot. I therefore spent considerable time updating the data_download option in cli.py and aligning it with the config.yaml file, which again came along with many updates in the tests.
