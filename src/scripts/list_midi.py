#!/usr/bin/env python

import rtmidi

midiin = rtmidi.MidiIn()
for m in midiin.get_ports():
    print("in", m)

midiout = rtmidi.MidiOut()
for m in midiin.get_ports():
    print("out", m)
