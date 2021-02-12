#!/usr/bin/env python

import os, sys
basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
print(lp)
sys.path.append(lp)


import time
from miditool import torso_sequencer
from rtmidi.midiutil import open_midiport
from miditool.sequencer import Sequencer

midiout, port = open_midiport(
    None,
    "TORSO",
    use_virtual=True,
    client_name="TORSO"
)
time.sleep(1)

seq = Sequencer(midiout, bpm=120, ppqn=10, loop=False, cols=4)
seq.add(0, 0)
# seq.add(1, 1)
seq.add(2, 2)
seq.add(3, 2)

try:
    seq.start()
    seq.join()
finally:
    seq.stop()
    midiout.close_port()
    del midiout

# t = torso_sequencer.TorsoSequencer(midiout=midiout)
#
# try:
#     t.start()
#     t.join()
# finally:
#     t.stop()
#     midiout.close_port()
#     del midiout
