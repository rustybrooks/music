#!/usr/bin/env python

from rtmidi.midiutil import open_midioutput, open_midiinput
import time

midiin = None
midiout = None


def callback(msg, data):
    # print(msg, data)
    midi_msg, offset = msg
    midiout.send_message(midi_msg)


def error_callback(*args, **kwargs):
    print(f"{args} - {kwargs}")


if __name__ == "__main__":
    midiout, port = open_midioutput(
        port=None,
        use_virtual=True,
        client_name="relay_out",
        port_name="relay_out",
    )

    midiin, port = open_midiinput(
        port=None,
        use_virtual=True,
        client_name="relay_in",
        port_name="relay_in",
    )

    midiin.set_callback(callback)
    midiin.set_error_callback(error_callback)
    print(f"Opened relay")

    while True:
        time.sleep(1)