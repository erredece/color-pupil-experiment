from eyelinkparser import EyeLinkParser, parse, defaulttraceprocessor

from datamatrix import (
    operations as ops,
    functional as fnc,
    series as srs,
    DataMatrix as DM,
    plot
)
from datamatrix.rbridge import lme4
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
import argparse, os

# Setting up a command argument to (re)parse the data if desired.
argparser = argparse.ArgumentParser(
    description="Data analysis script.")
argparser.add_argument('-p', '--parse', action="store_true", help="Parse all the files again. THIS WILL TAKE A LONG TIME!")
argparser.add_argument('-a', '--analyse', action="store_true", help="Analyses data again. THIS WILL TAKE A LONG TIME!")

args = argparser.parse_args()
path = os.getcwd() 

class CustomParser(EyeLinkParser):
    """A custom parser to start a phase at the start of a trial"""

    def on_start_trial(self):
        self.start_phase(['MSG', 0, 'start_phase', 'rsvp'])

def subset(dm):
    '''Selects a subset of columns'''
    dm = ops.keep_only(
        dm,
        dm.trialid,
        dm.ptrace_rsvp,
        dm.target_object,
        dm.tone_red,
        dm.tone_blue,
        dm.trial_correct,
        dm.path
    )

    '''
    Columns available: 
    ['arrow_correct', 'arrow_orientation', 'bright_blue_contrast', 'bright_red_contrast', 
    'dark_blue_contrast', 'dark_red_contrast', 'fixetlist_rsvp', 'fixstlist_rsvp', 'fixxlist_rsvp', 
    'fixylist_rsvp', 'gazed', 'gazed_left', 'gazed_right', 'path', 'pos_blue', 'pos_red', 
    'practicemode', 'ptrace_rsvp', 'pupil_size', 't_offset_rsvp', 't_onset_rsvp', 'target_letter', 
    'target_object', 'tone_blue', 'tone_red', 'trial_answer', 'trial_correct', 'trialid', 
    'ttrace_rsvp', 'xtrace_rsvp', 'ytrace_rsvp']
    '''

    return dm


@fnc.memoize(persistent=True)
def run():
    '''Parses the datamatrix'''
    dm = parse(parser=CustomParser, folder=path + "/data/", traceprocessor=defaulttraceprocessor(
        blinkreconstruct=True,  # Interpolate pupil size during blinks
        downsample=10), maxtracelen=1000) 
    dm = subset(dm)

    return dm

if args.parse: 
    print("Parsing again! This will take some time...") 
    run.clear()
else: 
    if os.path.isdir(path + "/.memoize/"):
        print("Using existing parsed data (unless new files have been added).")
    else: print("No existing directory with parsed data! Parsing files, this will take some time...")

dm = run()
print(dm)

dm.tone = "None"
for i in range(dm.length):
    if dm.target_object[i] == "blue":
        dm.tone[i] = dm.tone_blue[i]
    else:
        dm.tone[i] = dm.tone_red[i]

# Here we set up the baseline to remove NaN values
dm.pupil = srs.endlock(dm.ptrace_rsvp) 

dm.pupil = srs.baseline(
    series= dm.pupil,
    baseline=dm.ptrace_rsvp,
    bl_start=0,
    bl_end=2,
    method='subtractive'
)

# Splitting datamatrix between the two type of stimuli
blueDM, redDM = ops.split(dm.target_object, "blue", "red")

#Plots settings
mpl.rcParams['legend.frameon'] = False

# Plot for preprocessed trace
plt.figure()
plt.title('Preprocesed trace')
for tone, cdm in ops.split(redDM.tone_red):
    colour = "#FF3333" if tone == "bright" else "#8B0000"
    plot.trace(cdm.pupil, color=colour)
    
for tone, cdm in ops.split(blueDM.tone_blue):
    colour = "#00FFFF" if tone == "bright" else "#00008B"
    plot.trace(cdm.pupil, color=colour)

plt.tight_layout()
plt.savefig(path + "/preprocessed.png")
plt.clf()

# Splitting the tones in order to plot the pupil size changes.
brightBlueDM, darkBlueDM = ops.split(
    blueDM.tone_blue, "bright", "dark")
brightRedDM, darkRedDM = ops.split(
    redDM.tone_red, "bright", "dark")


def plot_series(x, s, color, label):
    '''Plots the time series of pupil changes'''

    se = s.std / np.sqrt(len(s))
    plt.fill_between(x, s.mean-se, s.mean+se, color=color, alpha=.25)
    plt.plot(x, s.mean, color=color, label=label)


# Plotting the pupil size changes
x = np.linspace(0, 11, dm.pupil.depth)

plt.figure()
plt.title("Changes in pupil size for each type of stimulus")
plt.xlim(0, 11)
plt.xticks(np.linspace(0, 11, 12))
plt.ylim(-500, 100)
plt.axvline(7, linestyle=':', color='grey', linewidth=1)
plt.axhline(1, linestyle=':', color='grey', linewidth=1)
plot_series(x, brightBlueDM.pupil, color='#00FFFF',
            label='Bright blue (N={0})'.format(len(brightBlueDM)))
plot_series(x, darkBlueDM.pupil, color='#00008B',
            label='Dark blue (N={0})'.format(len(darkBlueDM)))       
plot_series(x, brightRedDM.pupil, color='#FF3333',
            label='Bright red (N={0})'.format(len(brightRedDM)))
plot_series(x, darkRedDM.pupil, color='#8B0000',
            label='Dark red  (N={0})'.format(len(darkRedDM)))


plt.ylabel('Pupil size (norm)')
plt.xlabel('Trial length (s)')
legend = plt.legend(frameon=True, title='Stimulus type')
frame = legend.get_frame()
frame.set_facecolor("white")
plt.savefig(path + "/pupil_changes.png")
plt.clf()

print("Plotting completed. Proceeding with statistical analysis...")

# Statistical analysis

if args.analyse:
    print("Running statistical analysis! This will take some time...")
    run.clear()
else:
    if os.path.isdir(path + "/.memoize/"):
        print("Using existing analysed data (unless new files have been added).")
    else:
        print("No existing directory with analysed data! Analysing files, this will take some time...")

#lme4.verbose = True
model = 'pupil ~ target_object * tone + (1 + target_object * target_object | path)'
@fnc.memoize(persistent=True)
def analyse(dm, model):
    '''Analyses the parsed data'''
    lm = lme4.lmer_series(dm, model)
    return lm

lm = analyse(dm, model)
print(lm)

plt.figure()
plt.plot(lm.t[1], label='Colour', color='black')
plt.plot(lm.t[2], label='Brightness', color='#00FFFF')
plt.plot(lm.t[3], label='Interaction effect', color='#FF3333')
plt.axhline(0, color="grey", linewidth=1)
plt.axhline(2, color="grey", linestyle="dashed", linewidth=1)
plt.axhline(-2, color="grey", linestyle="dashed", linewidth=1)
legend = plt.legend(frameon=True, title='Factors')
frame = legend.get_frame()
frame.set_facecolor("white")
plt.title("T-Values for the experimental variables and their interaction across time.")
plt.xlabel("Point in time")
plt.ylabel("T-Value")
plt.show()
plt.savefig(path + "/stats.png")
plt.clf


# This below is code I used in order to get some statistical descriptives for the participant accuracy. 
# I am not fully sure if it will still work as I did it before the plotting, which lead to several changes in how I structured the data matrices.
# But I still keep it in case I need it in the future. 

'''
redCount, blueCount = 0, 0
scoreRed, scoreBlue = [], []

totalRed = dm.target_object._seq.count("red")
totalBlue = dm.target_object._seq.count("blue")
for answer in range(len(dm.trial_correct._seq)):
    if (answer + 1) % 180 == 0 and answer != 0:
        scoreRed.append(redCount / 180)
        scoreBlue.append(blueCount / 180)
        redCount, blueCount = 0, 0
    if dm.trial_correct._seq[answer] == 'True':
        if dm.target_object._seq[answer] == 'red':
            redCount += 1
        else:
            blueCount += 1

results = DM(length=len(scoreRed))
results.Red, results.Blue = "Red", "Blue"
for i in range(len(scoreRed)):
    results.Red[i] = scoreRed[i]
    results.Blue[i] = scoreBlue[i]

print("Red                 ", "Blue")
for i in range(len(scoreRed)):
    print(scoreRed[i], scoreBlue[i])

print(results)


print("Means and Stds: Red, then Blue")
print('Means: ', np.mean(results.Red._numbers), np.mean(results.Blue._numbers))
print('Stds: ', np.std(results.Red._numbers), np.std(results.Blue._numbers))
'''
print("Done!") # Just a notification to be completely sure it did run and everything went correctly.
