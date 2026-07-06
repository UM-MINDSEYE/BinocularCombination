from psychopy import visual, event, core
import numpy as np
import random
import os

SF = 0.03
PHASE_VAL = 0.0625
DEG_PER_PIX = SF * 360
RATIOS = [0.5, 1/np.sqrt(2), 1.0, np.sqrt(2), 2.0]
REPS = 8
CONFIGS = [1, 2]
STEP = 2

nonius_offset_x = 200
nonius_offset_y = 0
nonius_length = 50

win = visual.Window(size=[1200, 800], units='pix', color=[0, 0, 0], fullscr=False)

gabor_left = visual.GratingStim(win=win, size=100, sf=SF, ori=0)
gabor_right = visual.GratingStim(win=win, size=100, sf=SF, ori=0)
flanking_bar = visual.Rect(win=win, width=60, height=4, fillColor='black')

nonius_left = visual.ShapeStim(win, lineWidth=3, closeShape=False, lineColor='white')
nonius_right = visual.ShapeStim(win, lineWidth=3, closeShape=False, lineColor='white')

checker_l = visual.ImageStim(win, image="../stimuli/checker_boarder.png", size=(120,120))
checker_r = visual.ImageStim(win, image="../stimuli/checker_boarder.png", size=(120,120))

def build_vertices(offset_x, offset_y, length):
    lv = ((-offset_x, offset_y), (-offset_x, offset_y + length),
          (-offset_x, offset_y), (-offset_x - length, offset_y))
    rv = ((offset_x, -offset_y), (offset_x, -offset_y - length),
          (offset_x, -offset_y), (offset_x + length, -offset_y))
    return lv, rv

def run_calibration_screen(x, y, length, trial_num=None):
    calibrating = True
    while calibrating:
        keys = event.getKeys()
        if 'escape' in keys:
            core.quit()
        if 'space' in keys:
            calibrating = False

        if 'up' in keys:
            y += STEP
        if 'down' in keys:
            y -= STEP
        if 'left' in keys:
            x -= STEP
        if 'right' in keys:
            x += STEP

        lv, rv = build_vertices(x, y, length)
        nonius_left.vertices = lv
        nonius_right.vertices = rv
        checker_l.pos = (-x, y)
        checker_r.pos = (x, -y)

        checker_l.draw()
        checker_r.draw()
        nonius_left.draw()
        nonius_right.draw()

        win.flip()
    return x, y

trial_list = []
for r in RATIOS:
    for c in CONFIGS:
        for _ in range(REPS):
            trial_list.append({'ratio': r, 'config': c})
random.shuffle(trial_list)

results = []

for t_idx, trial in enumerate(trial_list):

    nonius_offset_x, nonius_offset_y = run_calibration_screen(nonius_offset_x, nonius_offset_y, nonius_length, t_idx + 1)

    delta = trial['ratio']
    c_left = (2 * delta / (1 + delta)) * 0.5
    c_right = (2 / (1 + delta)) * 0.5
    p_left, p_right = (-PHASE_VAL, PHASE_VAL) if trial['config'] == 1 else (PHASE_VAL, -PHASE_VAL)

    gabor_left.contrast, gabor_left.phase = c_left, p_left
    gabor_right.contrast, gabor_right.phase = c_right, p_right

    gabor_left.pos = (-nonius_offset_x, nonius_offset_y)
    gabor_right.pos = (nonius_offset_x, -nonius_offset_y)
    flanking_bar.pos = (nonius_offset_x + 120, 0)

    while True:
        gabor_left.draw()
        gabor_right.draw()
        flanking_bar.draw()
        win.flip()

        keys = event.getKeys(keyList=['up', 'down', 'return', 'escape'])

        if 'up' in keys:
            flanking_bar.pos += (0, 1)
        if 'down' in keys:
            flanking_bar.pos -= (0, 1)
        if 'return' in keys:
            phi_a = flanking_bar.pos[1] * DEG_PER_PIX
            results.append([t_idx + 1, delta, trial['config'], phi_a])
            break
        if 'escape' in keys:
            core.quit()

if not os.path.exists("../data"):
    os.makedirs("../data")

np.savetxt("../data/baseline_full_data.csv", results, delimiter=",",
           header="trial,ratio,config,perceived_phase", comments='')

print(f"Finished! Offsets ended at X:{nonius_offset_x}, Y:{nonius_offset_y}")
win.close()
core.quit()