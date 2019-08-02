from eyelinkparser import EyeLinkParser, parse, defaulttraceprocessor

from datamatrix import (
    operations as ops,
    functional as fnc,
    series as srs,
    DataMatrix as DM,
    plot
)
from datamatrix.rbridge import lme4
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import argparse, os, operator

# Setting up a command argument to (re)parse the data if desired.
argparser = argparse.ArgumentParser(
    description="Data analysis script.")
argparser.add_argument('-p', '--parse', action="store_true", help="Parse all the files again. THIS WILL TAKE A LONG TIME!")

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
    dm.blockID,
    dm.trialid,
    dm.block_condition,
    dm.correct_selection,
    dm.loop_rt,
    dm.subject_nr
    )

    '''Columns available: 
    ['acc', 'accuracy', 'average_response_time', 'avg_rt', 'background', 'bidi', 'blockID', 'blockOrder', 'block_condition', 
    'canvas_backend', 'checkFix', 'clock_backend', 'color_backend', 'compensation', 'coordinates', 'correct', 'correct_block_feedback', 
    'correct_feedback', 'correct_keyboard_response', 'correct_selection', 'correct_sketchpad', 'count_README', 'count_add_block', 
    'count_blank', 'count_block_feedback', 'count_default_settings', 'count_eight_options', 'count_exp_sequence', 'count_experiment', 
    'count_experiment_settings', 'count_eye_tracker', 'count_feedback', 'count_final_feedback', 'count_form_base', 'count_get_input', 
    'count_globals', 'count_item', 'count_itemArray', 'count_keyboard_response', 'count_logger', 'count_new_inline_script', 'count_new_loop', 
    'count_new_quest_staircase_init', 'count_new_quest_staircase_next_1', 'count_pygaze_init', 'count_pygaze_log', 'count_pygaze_start_recording', 
    'count_pygaze_stop_recording', 'count_python_definitions', 'count_select_target', 'count_sketchpad', 'count_smoothing', 'count_speak_target', 
    'count_speech', 'count_startup_variables', 'count_trial', 'datetime', 'description', 'disable_garbage_collection', 'ecc', 'experiment_file', 
    'experiment_path', 'eye_used', 'final_acc', 'final_rt', 'fixetlist_rsvp', 'fixstlist_rsvp', 'fixxlist_rsvp', 'fixylist_rsvp', 'font_bold', 
    'font_family', 'font_italic', 'font_size', 'font_underline', 'foreground', 'form_clicks', 'form_response', 'fullscreen', 'height', 'itemIds', 
    'keyboard_backend', 'likelihoodThr', 'live_row', 'live_row_eight_options', 'live_row_new_loop', 'logfile', 'loop_rt', 'mode2', 'mouse_backend', 
    'numberOfTrials', 'opensesame_codename', 'opensesame_version', 'opt8', 'path', 'practiceMode', 'psychopy_screen', 'ptrace_rsvp', 'quest_test_value', 
    'repeat_cycle', 'response', 'response_block_feedback', 'response_feedback', 'response_final_feedback', 'response_keyboard_response', 'response_sketchpad', 
    'response_time', 'response_time_block_feedback', 'response_time_feedback', 'response_time_final_feedback', 'response_time_keyboard_response', 
    'response_time_sketchpad', 'round_decimals', 'rounds', 'sampler_backend', 'showCue', 'size', 'sound_buf_size', 'sound_channels', 'sound_freq', 
    'sound_sample_size', 'stabilize', 'staircase', 'start', 'subject_nr', 'subject_parity', 'synth_backend', 't_offset_rsvp', 't_onset_rsvp', 
    'target', 'time_README', 'time_add_block', 'time_blank', 'time_block_feedback', 'time_default_settings', 'time_eight_options', 'time_exp_sequence', 
    'time_experiment', 'time_experiment_settings', 'time_eye_tracker', 'time_feedback', 'time_final_feedback', 'time_form_base', 'time_get_input', 'time_globals', 
    'time_item', 'time_itemArray', 'time_keyboard_response', 'time_logger', 'time_new_inline_script', 'time_new_loop', 'time_new_quest_staircase_init', 
    'time_new_quest_staircase_next_1', 'time_pygaze_init', 'time_pygaze_log', 'time_pygaze_start_recording', 'time_pygaze_stop_recording', 
    'time_python_definitions', 'time_select_target', 'time_sketchpad', 'time_smoothing', 'time_speak_target', 'time_speech', 'time_startup_variables', 
    'time_trial', 'title', 'total_acc', 'total_correct', 'total_response_time', 'total_responses', 'total_rt', 'transparent_variables', 'trialCounter', 
    'trialThreshold', 'trialThresholdOption', 'trialid', 'ttrace_rsvp', 'uniform_coordinates', 'width', 'winner', 'xtrace_rsvp', 'ytrace_rsvp']
    '''

    return dm


@fnc.memoize(persistent=True)
def run():
    '''Parses the datamatrix'''
    dm = parse(folder=path + "/data/", traceprocessor=defaulttraceprocessor(
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
print(dm.column_names)

bwCondition, colourCondition = ops.split(dm.block_condition, 0, 1)

def ttest(var1, var2):
    '''Runs a t-test between two variables'''
    mean1 = np.mean(var1)
    mean2 = np.mean(var2)
    vari1 = np.var(var1)
    vari2 = np.var(var2)
    sd1 = np.sqrt(vari1)
    sd2 = np.sqrt(vari2)
    len1 = len(var1)
    len2 = len(var2)
    print("Performing T-Test with the following parameters:")
    print("Variable 1 - Mean: {0} SD: {1} N: {2} CV: {3}".format(mean1, sd1, len1, sd1/mean1))
    print("Variable 2 - Mean: {0} SD: {1} N: {2} CV: {3}".format(mean2, sd2, len2, sd2/mean2))
    ttest = (mean1 - mean2) / np.sqrt(vari1/len1 - vari2/len2)
    print("Result: {0}".format(ttest))
    return ttest

def getRTs(condition):
    '''Obtains the mean RTs for each participant'''
    RT = []
    responses = []
    trials = 0
    for trial in range(len(condition)):
        responses.append(condition.loop_rt[trial])
        trials += 1
        if trial == len(condition) - 1 or trial < len(condition) - 1 and condition.subject_nr[trial] != condition.subject_nr[trial + 1]:
            RT.append(np.mean(responses))
            responses = []
            trials = 0
    return RT

bwRT = getRTs(bwCondition)
colourRT = getRTs(colourCondition)

print("T-Test RTs")
RT_ttest = ttest(bwRT, colourRT)

def getAccuracies(condition):
    '''Obtains the accuracy for each participant'''
    accuracy = []
    correct = 0
    trials = 0
    for trial in range(len(condition)):
        correct = correct + condition.correct_selection[trial]
        trials += 1
        if trial == len(condition) - 1 or trial < len(condition) - 1 and condition.subject_nr[trial] != condition.subject_nr[trial + 1]:
            #print("Appending for subject {0}".format(condition.subject_nr[trial]))
            accuracy.append(correct / trials)
            correct, trials = 0, 0
    return accuracy

bwAccuracies = getAccuracies(bwCondition)
colourAccuracies = getAccuracies(colourCondition)

print("T-Test Accuracy")
acc_tttest = ttest(bwAccuracies, colourAccuracies)

def rearrange(array1, array2):
    '''Rearranges the arrays by sorting the first one while still matching it with the other condition'''
    shared = []
    for i in range(len(array1)):
        shared.append((array1[i], array2[i]))
    
    shared.sort(key = operator.itemgetter(0))
    array1, array2 = [], []
    for i in range(len(shared)):
        array1.append(shared[i][0])
        array2.append(shared[i][1])
    
    return array1, array2


bwRT, colourRT = rearrange(bwRT, colourRT)

accuracy = []

for i in range(len(bwAccuracies)):
    accuracy.append((bwAccuracies[i], colourAccuracies[i]))

accuracy.sort(key = operator.itemgetter(0))

accuracyChange = []
for i in range(len(accuracy)):
    accuracyChange.append((accuracy[i][1] - accuracy[i][0]) / accuracy[i][0] * 100)

print("Overall mean accuracy change: {0}".format(np.mean(accuracyChange)))

bwAccuracies, colourAccuracies = [], []
x = np.linspace(1, len(accuracy), num=len(accuracy))

for i in range(len(accuracy)):
    bwAccuracies.append(accuracy[i][0])
    colourAccuracies.append(accuracy[i][1])

mpl.rcParams['legend.frameon'] = False
plt.figure()
plt.title("Mean accuracy between subjects for each condition")
plt.plot(x, bwAccuracies, 'ko', label="Black and white")
plt.plot(x, colourAccuracies, 'ro', label="Red and blue")
#plt.plot(x, accuracyChange, color= "orange", label="Increment" )
plt.xticks(x)
plt.yticks(np.linspace(0.1, 1, num=10))
plt.xlabel("Subject number")
plt.ylabel("Correct response ratio")
legend = plt.legend(frameon=True, title='Condition')
frame = legend.get_frame()
frame.set_facecolor("white")
plt.tight_layout()
plt.savefig(path + "/accuracy.png")
plt.clf()

plt.figure()
plt.title("Mean response time between conditions")
plt.plot(x, bwRT, 'ko', label="Black and white")
plt.plot(x, colourRT, 'ro', label="Red and blue")

plt.xticks(x)
#plt.yticks(np.linspace(0.1, 1, num=10))
'''
plt.axhline(np.mean(dm.loop_rt._numbers), color='grey', linewidth=1)
plt.axhline(np.mean(dm.loop_rt._numbers) + 2*np.std(dm.loop_rt._numbers),
            color='grey', linestyle='dashed', linewidth=1)
plt.axhline(np.mean(dm.loop_rt._numbers) - 2*np.std(dm.loop_rt._numbers),
            color='grey', linestyle='dashed', linewidth=1)'''
legend = plt.legend(frameon=True, title='Condition')
frame = legend.get_frame()
frame.set_facecolor("white")
plt.xlabel("Subject number")
plt.ylabel("Response time (seconds)")
plt.tight_layout()
plt.savefig(path + "/rt.png")
plt.clf()
