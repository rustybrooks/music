#!/usr/bin/env python

import os, sys
basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
print(lp)
sys.path.append(lp)


import time
from miditool import torso_sequencer
from rtmidi.midiutil import open_midiport

midiout, port = open_midiport(
    None,
    "output",
    use_virtual=True,
    client_name="TORSE"
)
time.sleep(1)

t = torso_sequencer.TorsoSequencer(midiout=midiout)

try:
    t.start()
    t.join()
finally:
    t.stop()
    midiout.close_port()
    del midiout
