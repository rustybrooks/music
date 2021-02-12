#!/usr/bin/env python

import os, sys
basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
print(lp)
sys.path.append(lp)


import time
from miditool import torso_sequencer, notes
from rtmidi.midiutil import open_midiport
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from miditool.sequencer import Sequencer


midiout, port = open_midiport(
    None,
    "TORSO",
    use_virtual=True,
    client_name="TORSO"
)
time.sleep(1)

tt = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['F', 4])],
    pulses=5,
)

snotes = tt.generate()
print(snotes)

seq = Sequencer(midiout, bpm=220, ppqn=240)
for i, el in enumerate(snotes):
    if not el:
        continue

    # track should probably generate these events
    seq.add(event=[NOTE_ON+tt.channel, el[0], el[2]], tick=seq.ppqn*(i + tt.offset))
    seq.add(event=[NOTE_OFF+tt.channel, el[0], 0], tick=seq.ppqn*(i+tt.sustain + tt.offset))

time.sleep(10)

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
