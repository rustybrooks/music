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

tt1 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['D#', 3])],
    pulses=4,
    steps=6,
    division=2,
)
tt2 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['C#', 3])],
    pulses=9,
    steps=16,
)
tt3 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['D#', 2])],
    pulses=5,
    division=2,
)

t = torso_sequencer.TorsoSequencer(
    midiout=midiout,
    lookahead=0.02,
    bpm=120,
)

t.add_track(track_name='hihat', track=tt1)
t.add_track(track_name='cymbal', track=tt2)
t.add_track(track_name='clap', track=tt3)

try:
    t.start()
    t.join()
finally:
    t.stop()
    midiout.close_port()
    del midiout
