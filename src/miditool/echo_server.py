#!/usr/bin/env python

from rtmidi.midiutil import open_midioutput
import argparse
import rtmidi
import time

midis = {}
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
        midi_ports = midiin.get_ports()
        midi_matches = [x for x in enumerate(midi_ports or []) if x[1] and name in x[1]]
        if midi_matches:
            break

        time.sleep(2)

    midi_device = midi_matches[0]
    midis[name] = midiin.open_port(midi_device[0], name=midi_device[1])
    midis[name].set_callback(callback)
    midis[name].set_error_callback(error_callback)
    print(f"Opened {name}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("target", help="Input MIDI device to listen for")
    p.add_argument(
        "-o",
        "--output",
        default=None,
        help="MIDI device to send output to (if not specified uses virtual output)",
    )
    args = p.parse_args()

    midiout = rtmidi.MidiOut()

    if args.output is not None:
        all_ports = midiout.get_ports()
        print(all_ports)
        matches = [x for x in enumerate(all_ports) if "Studio" in x[1]]
        device = matches[0]
        midiout = midiout.open_port(device[0], name=device[1])
        print("opening device", device)
    else:
        midiout, port = open_midioutput(
            port=None,
            use_virtual=True,
            client_name="echo server",
            port_name="echo server",
        )

    midiin = rtmidi.MidiIn()
    open_midi(args.target)

    while True:
        ports = midiin.get_ports()
        # print(ports)
        for k, v in midis.items():
            # print(f"{k} in ports? {k in ports}")
            if k not in ports:
                v.close_port()
                open_midi(k)

        time.sleep(1)
