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
    pulses=9,
)
tt2 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['C#', 3])],
    pulses=4,
)
tt3 = torso_sequencer.TorsoTrack(
    notes=[notes.note_to_number(['D#', 2])],
    pulses=5,
)

if 0:

    t1 = time.time()
    snotes = tt.generate()
    print(1000*(time.time()-t1), snotes)

    seq = Sequencer(midiout, bpm=320, ppqn=240)
    for el in snotes:
        tick, event = el
        seq.add(event=event, tick=(tick*seq.ppqn))

    try:
        seq.start()
        seq.join()
    finally:
        seq.stop()
        midiout.close_port()
        del midiout
else:
    t = torso_sequencer.TorsoSequencer(
        midiout=midiout,
        lookahead=0.02,
        bpm=400,
    )

    t.add_track(track_name='hihat', track=tt1)
    t.add_track(track_name='snare', track=tt2)
    t.add_track(track_name='clap', track=tt3)

    try:
        t.start()
        t.join()
    finally:
        t.stop()
        midiout.close_port()
        del midiout
