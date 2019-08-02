# color-pupil-experiment
Experiments on determining if covert attention on red and blue backgrounds trigger a pupillary response. Experiment 1 is a Posner cuing task, while Experiment 2 is a performance comparison between the Mind Writing Pupil (see https://github.com/smathot/mind-writing-pupil) and a variation using red and blue backgrounds.

Information and data from the experiments are available in their OSF directory: https://osf.io/cztre/?view_only=9421a1da29c94ef6820266898676dd0f

## Procedure

This is done by running the `.osexp` files in OpenSesame 3 (https://osdoc.cogsci.nl/). For Experiment 1, the `letters` directory with its contents must be in the same directory than the `.osexp` file. Experiment 2 requires the `__pool__` and `resources` directories with their contents to be in the same directory than the `.oesxp` file. 

This experiment is setup to be run in an EyeLink 1000 eye tracker. Thus the data will be dumped in EDF format, which is then converted to ASC with the tool provided by the EyeLink. 

## Analysis

The analysis Python script will parse all ASC files. This takes some time, but generally it only has to be done once as it's stored. If it is required to parse again, the argument `-p` can be added when running the script. This script will produce the same plots that can be found and the images directory for each experiment, as well as performing the necessary statistical analysis. 
