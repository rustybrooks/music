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

t = torso_sequencer.TorsoSequencer(
    midiout=midiout,
    lookahead=0.02,
    bpm=60,
)

"""
tt1 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['C', 3])],
    pulses=16,
    steps=16,
    division=2,
    accent=0,
    velocity=127,
    timing=.5,
)
tt2 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['E', 3])],
    pulses=8,
    division=2,
    steps=16,
)
tt3 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['G', 2])],
    pulses=8,
    division=2,
    steps=16,
    accent=0,
    velocity=127,
    repeats=3,
    time=4,
    offset=.2,
    # delay=0.25,
)

t.add_track(track_name='hihat', track=tt1)
t.add_track(track_name='cymbal', track=tt2)
t.add_track(track_name='clap', track=tt3)
"""

tp = torso_sequencer.TorsoTrack(
    notes=[('C', 4), ('E', 4), ('G', 4), ('B', 4)],
    pulses=11,
    steps=16,
    repeats=5,
    repeat_time=6,
    sustain=1,
    style=1,
)
t.add_track(track_name='piano', track=tp)

try:
    t.start()
    t.join()
finally:
    t.stop()
    midiout.close_port()
    del midiout
