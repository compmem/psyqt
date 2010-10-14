"""
The PsyQt wish-list example.
"""

# load everything for ease
from psyqt import *

@serial_group
def y_resp(s):
    hide(s, update_screen=False)
    show(Text('Awesome!'),duration=2000)
    show(Text("Keep it comin'!"),duration=2000)

@parallel_group
def n_resp(s):
    with serial():
        hide(s, update_screen=False)
        show(Text('Bummer!\nPress any key to quit.'),duration=2000)
    with serial():
        key_choice([])
        quit_exp()

# Show a word and wait for a Y/N like/dislike response
words = ['jubba','wubba','lubba']
for w in words:
    with parallel():
        # show the word in the center of the screen
        s = show(Text(w),loc=(.5,.5))
        with serial():
            # wait for 250ms before accepting responses
            wait(250)
            resp = key_choice(['Y':y_resp(s),'N':n_resp(s)],max_duration=5000)

    # pause before next stim
    wait(500, connect_to=resp.Y)

# run the experiment
run()
