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
import rtmidi
from miditool.sequencer import Sequencer

virtual = False

if virtual:
    midiout, port = open_midiport(
        None,
        "TORSO",
        use_virtual=True,
        client_name="TORSO"
    )
else:
    midiout = rtmidi.MidiOut()
    all_ports = midiout.get_ports()
    print(all_ports)
    matches = [x for x in enumerate(all_ports) if "MIDI4x4:MIDI4x4 MIDI" in x[1]]
    device = matches[0]
    midiout = midiout.open_port(device[0], name=device[1])

time.sleep(1)

t = torso_sequencer.TorsoSequencer(
    midiout=midiout,
    lookahead=0.02,
    bpm=60,
)

tp = torso_sequencer.TorsoTrack(
    notes=[
        ('C', 4),
        ('E', 4),
        ('G', 4),
        # ('B', 4)
    ],
    pulses=16,
    steps=16,
    repeats=2,
    # repeat_time=6,
    sustain=1,
    style=1,
    voicing=3,
)
t.add_track(track_name='piano', track=tp)

try:
    t.start()
    t.join()
finally:
    t.stop()
    midiout.close_port()
    del midiout
