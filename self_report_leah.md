## What task was assigned to you when you started?
My task was to integrate the option of reading from a config file.
Also, which was not I think outspoken, but since I was the one with the most experience in GitHub, my task was also to set up and manage the GitHub Repo, merging the individual tasks and be of help in this regard. 

## What changed during the implementation, that is, what is the outcome of the project?
I have never done any CLI-Tool or Package so this was new to me and I also didn't know how much work integrating a config file would mean (ChatGPT said something about 400 lines of code?). As it *surprisingly* turned out ChatGPT was absolutely wrong about the estimate. Adding the option of a config file is in it self not so code intensive. However, I had to merge the whole CLI logic from sys.arg to argparse, change tests, refactor and added a logic to use config file and CLI-Inputs together.

For the Joint-Task we decided on automated-data download since this would be a very nice addition to my team members contributions. I programmed the backbone of this and then had the others look more throughout through the code, making sure it makes sense, works, document it and test it.

## What was the biggest challenge you faced in the implementation?
My first challenge was, that I had to rewrite CLI-Part of the existing package from sys.arg to argparse. Never really having worked with CLI-based programms that was very interesting to learn. 
Another challenge was to write test now, especially for when CLI and Config were used together. I found the conftest.py file in the package which was of great help and is something I haven't worked with jet.

For the joint task about the automated-data-download a challenge was to have the option of using downloaded-data or an already existing datafile as well as integrating a cache to reuse a already downloaded dataset.
A challenge was as well to structure the code logically in the end, but I am quite happy with how it turned out.
Understanding why tests fail is always a challenge.

A challenge I encountered was also working together as a team *correctly* with GitHub. 
Getting everyone correctly working with GitHub was more of a challenge then I thought.
There I see that I should have done a better job teaching the principles of GitHub in the very beginning. But, circumstances out of my control, a 3 weeks Christmas break and other projects where not helping to have an in person GitHub-Bootcamp.

## What was the biggest challenge when merging everyone’s work into one package?
Since we used version control merging was not a problem. Actually surprisingly little of a problem. The biggest problem in the beginning was to rebase in VS Code. I previously only really done rebases where I needed to merge commits together in IntelliJ which provided a nice interface for it. But once this was understood it was a smooth ride.
Sometimes tests would fail after a merge. This can be very time consuming.


