#!/usr/bin/env python

from rtmidi.midiutil import open_midioutput
import rtmidi
import sys
import time

midis = {

}
midiin = None


def callback(msg, data):
    # print(msg, data)
    midi_msg, offset = msg
    midiout.send_message(midi_msg)


def error_callback(*args, **kwargs):
    print(f"{args} - {kwargs}")


def open_midi(name):
    print(f"Opening {name}")
    while True:
        ports = midiin.get_ports()
        matches = [x for x in enumerate(ports or []) if x[1] and name in x[1]]
        if matches:
            break

        time.sleep(2)

    device = matches[0]
    midis[name] = midiin.open_port(device[0], name=device[1])
    midis[name].set_callback(callback)
    midis[name].set_error_callback(error_callback)
    print(f"Opened {name}")


if __name__ == '__main__':
    midiout = rtmidi.MidiOut()

    all_ports = midiout.get_ports()
    print(all_ports)
    matches = [x for x in enumerate(all_ports) if 'Studio' in x[1]]
    device = matches[0]
    print("opening device", device)
    midiout = midiout.open_port(device[0], name=device[1])


    midiin = rtmidi.MidiIn()

    target = sys.argv[1]
    open_midi(target)

    while(True):
        ports = midiin.get_ports()
        # print(ports)
        for k, v in midis.items():
            # print(f"{k} in ports? {k in ports}")
            if k not in ports:
                v.close_port()
                open_midi(k)

        time.sleep(1)