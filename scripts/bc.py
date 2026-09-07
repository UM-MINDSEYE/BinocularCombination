from psychopy import visual, event, core
import numpy as np
import random
import os
from datetime import datetime

SF = 0.03
PHASE_VAL = 0.0625
DEG_PER_PIX = SF * 360
RATIOS = [0.5, 1/np.sqrt(2), 1.0, np.sqrt(2), 2.0]
REPS = 6
CONFIGS = [1, 2]
STEP = 2

nonius_offset_x = 600
nonius_offset_y = 0
nonius_length = 50

win = visual.Window(size=[1200, 800], units='pix', color=[0, 0, 0], fullscr=True)

gabor_left = visual.GratingStim(win=win, size=100, sf=SF, ori=90)
gabor_right = visual.GratingStim(win=win, size=100, sf=SF, ori=90)
flanking_bar_left = visual.Rect(win=win, width=100, height=2, fillColor='black')
flanking_bar_right = visual.Rect(win=win, width=100, height=2, fillColor='black')

nonius_left = visual.ShapeStim(win, lineWidth=3, closeShape=False, lineColor='white')
nonius_right = visual.ShapeStim(win, lineWidth=3, closeShape=False, lineColor='white')

checker_l = visual.ImageStim(win, image="../stimuli/checker_boarder.png", size=(120,120))
checker_r = visual.ImageStim(win, image="../stimuli/checker_boarder.png", size=(120,120))

# >>> Scrambled frame & vertical line
tex_size = 256
block_size = 7
n_blocks = tex_size // block_size

small_noise = np.random.choice([-1, 1], size=(n_blocks, n_blocks))
noise = np.kron(small_noise, np.ones((block_size, block_size)))

mask = np.ones((tex_size, tex_size))
center_px = 107
mid = tex_size // 2
mask[
    mid - center_px : mid + center_px,
    mid - center_px : mid + center_px
] = -1

frame_l = visual.GratingStim(win=win, tex=noise, mask=mask, size=120, interpolate=False)
frame_r = visual.GratingStim(win=win, tex=noise, mask=mask, size=120, interpolate=False)

vertical_line_l = visual.Rect(win=win, width=2, height=100, fillColor='black')
vertical_line_r = visual.Rect(win=win, width=2, height=100, fillColor='black')
# <<<


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
        frame_l.pos = (-x, y)
        frame_r.pos = (x, -y)
        
        frame_l.draw()
        frame_r.draw()
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
    frame_l.pos = (-nonius_offset_x, nonius_offset_y)
    frame_r.pos = (nonius_offset_x, -nonius_offset_y)
    flanking_bar_left.pos = (-nonius_offset_x, 0)
    flanking_bar_right.pos = (nonius_offset_x, 0) # jlb: (nonius_offset_x + 120, 0)
    vertical_line_l.pos = (-nonius_offset_x, nonius_offset_y)
    vertical_line_r.pos = (nonius_offset_x, -nonius_offset_y)

    while True:
        gabor_left.draw()
        gabor_right.draw()
        frame_l.draw()
        frame_r.draw()
        flanking_bar_left.draw()
        flanking_bar_right.draw()
        vertical_line_l.draw()
        vertical_line_r.draw()
        
        win.flip()

        keys = event.getKeys(keyList=['up', 'down', 'space', 'escape'])

        if 'up' in keys:
            flanking_bar_left.pos += (0, 1)
            flanking_bar_right.pos += (0, 1)
        if 'down' in keys:
            flanking_bar_left.pos -= (0, 1)
            flanking_bar_right.pos -= (0, 1)
        if 'space' in keys:
            phi_a = flanking_bar_left.pos[1] * DEG_PER_PIX
            results.append([t_idx + 1, delta, trial['config'], phi_a])
            break
        if 'escape' in keys:
            core.quit()

if not os.path.exists("../data"):
    os.makedirs("../data")

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
np.savetxt(f'../data/baseline_full_data_{timestamp}.csv', results, delimiter=",",
           header="trial,ratio,config,perceived_phase", comments='')

print(f"Finished! Offsets ended at X:{nonius_offset_x}, Y:{nonius_offset_y}")
win.close()
core.quit()