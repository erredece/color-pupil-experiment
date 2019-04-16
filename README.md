# color-pupil-experiment
Experiment on determining if covert attention on red and blue backgrounds trigger a pupillary response. 

Information and data from the experiment are available in its OSF directory: https://osf.io/cztre/?view_only=9421a1da29c94ef6820266898676dd0f

## Procedure

This is done by running the .osexp file in OpenSesame (https://osdoc.cogsci.nl/). The letters directory and its contents must be in the same directory than this file.

This experiment is setup to be run in an EyeLink 1500 eyetracker. Thus the data will be dumped in EDF format, which is then converted to ASC with the tool provided by the EyeLink. 

## Analysis

The analysis Python script will parse all ASC files. This takes some time, but generally it only has to be done once as it's stored. If it is required to parse again, the argument -p can be added when running the script. This script will produce plots for preprocessed pupil trace and pupil trace across time. 

