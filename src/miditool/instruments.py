import copy
import rtmidi
from itertools import accumulate


note_list = {
    "sharp": ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    "flat": ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
}

scales = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "natural_minor": [2, 1, 2, 2, 1, 2, 2],
    "harmonic_minor": [2, 1, 2, 2, 1, 3, 1],
    "melodic_minor": [2, 1, 2, 2, 2, 2, 1],
    "hungarian_minor, ": [2, 1, 3, 1, 1, 3, 1],
    "neapolitan_minor": [1, 2, 2, 2, 2, 2, 1],
    "neapolitan_major": [1, 2, 2, 2, 2, 2, 1],
    "pentatonic_major": [2, 2, 3, 2, 3, ],
    "pentatonic_minor": [3, 2, 2, 3, 2, ],
    "whole_tone": [2, 2, 2, 2, 2, 2, ],
    "diminished": [2, 1, 2, 1, 2, 1, 2, 1],
    "enigmatic": [1, 3, 2, 2, 2, 1, 1],
    "chromatic": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "ionian": [2, 2, 1, 2, 2, 2, 1],
    "dorian": [2, 1, 2, 2, 2, 1, 2],
    "phrygian": [1, 2, 2, 2, 1, 2, 2],
    "lydian": [2, 2, 2, 1, 2, 2, 1],
    "mixolydian": [2, 2, 1, 2, 2, 1, 2],
    "aeolian": [2, 1, 2, 2, 1, 2, 2],
    "aeoliant": [1, 2, 2, 1, 2, 2, 2],
}


def note_to_number(n):
    note, octave = n
    i = note_list['sharp'].index(note.upper())
    if i == -1:
        i = note_list['flat'].index(note.upper())

    return 36 + octave*12 + i


def number_to_note(n, is_sharp=True):
    return [note_list['sharp' if is_sharp else 'flat'][n % 12], (n-36) // 12]


class Instrument:
    def __init__(self, in_rule=None, out_rule=None, callback=None):
        if in_rule:
            callback = callback or [self.input_callback, {}]

            midiin = rtmidi.MidiIn()
            label, index = in_rule
            matches = [x for x in enumerate(midiin.get_ports()) if label in x[1]]
            device = matches[index]
            self.midi_in = midiin.open_port(device[0], name=device[1])
            self.midi_in.set_callback(*callback)

        if out_rule:
            midiout = rtmidi.MidiOut()
            label, index = out_rule
            matches = [x for x in enumerate(midiout.get_ports()) if label in x[1]]
            device = matches[index]
            self.midi_out = midiout.open_port(device[0], name=device[1])

    @classmethod
    def input_callback(cls, msg, data):
        midi_message, offset = msg
        status, b1, b2 = midi_message
        print(f"{status:x} {b1} {b2} - {data}")

    def send_message(self, status, b1, b2):
        self.midi_out.send_message([status, b1, b2])


class Launchpad(Instrument):
    def __init__(self, index=0, callback=None):
        super().__init__(
            in_rule=['Launchpad', index],
            out_rule=["Launchpad", index],
            callback=callback,
        )
        self.index = index
        self.clear()

        print(f"Launchpad {index} ready")

    def clear(self):
        for i in range(9):
            self.send_cc(i, 0)
            self.send_cc2(i, 0)

        for x in range(10):
            for y in range(9):
                self.send_note_on(x, y, 0)

    def __del__(self):
        self.clear()

    def send_note_on(self, x, y, value):
        self.send_message(0x90, y*16+x, value)

    def send_cc(self, button, value):
        self.send_message(0xb0, 104+button, value)

    def send_cc2(self, button, value):
        self.send_note_on(8, button, value)


class MultiLaunchpadModes:
    pass


class MLMPianoMode(MultiLaunchpadModes):
    def __init__(self):
        self.mlp = None
        self.scale_notes = None

    def start(self, mlp):
        self.mlp = mlp
        self.scale = 'pentatonic_minor'

        self.scale_notes = list(accumulate(scales[self.scale], lambda x, y: x+y, initial=0))
        self.off_notes = [x for x in range(12) if x not in self.scale_notes]
        self.scale_map = []
        self.off_map = []

        this = 0
        for n in scales[self.scale]:
            interval = n-1
            self.scale_map.append(this)

            for i in range(interval):
                self.off_map.append(this+i)
            this += max(interval, 1)

        self.scale_map.append(this)
#        for i in range(12-this):
#            self.off_map.append(this+i+1)

        # print(self.scale_notes, self.off_notes)
        print(self.off_map)
        print(self.scale_map)

        for y in range(0, 8, 2):
            for x in self.scale_map:
                self.mlp.send_note_on(x, y+1, 127)

            for x in self.off_map:
                self.mlp.send_note_on(x, y, 83)

    def callback(self, msg, data):
        midi_msg, offset = msg
        message = self.mlp.callback_decoder(midi_msg, data)

        if message[0] in [
            'NoteOn',
            # 'NoteOff'
        ]:
            x, y = message[1:3]
            root = note_to_number(['C', 0])
            if y % 2 == 1:
                if x in self.scale_map:
                    noten = root + self.scale_notes[x] + 12*(y//2)
                    print(x, y, noten, number_to_note(noten))

            else:
                if x in self.off_map:
                    max_scale_n = max([n for n in self.scale_map if n <= x])
                    noten = root + self.scale_notes[max_scale_n] + (x - max_scale_n + 1) + 12*(y//2)
                    print(x, y, noten, number_to_note(noten))


class MultiLaunchpad:
    def __init__(self, number=2, callback_data=None, modes=None, start_mode=0):
        self.modes = modes or [MLMPianoMode()]
        self.mode = modes[start_mode]

        if callback_data is None:
            callback_data = [{} for i in range(number)]
        if not isinstance(callback_data, (list, tuple)):
            callback_data = [copy.deepcopy(callback_data) for i in range(number)]

        for i, d in enumerate(callback_data):
            d.update({'index': i})

        self.launchpads = [
            Launchpad(
                index=i,
                callback=[self.mode.callback, callback_data[i]]
            ) for i in range(number)
        ]

        self.mode.start(self)

    @classmethod
    def callback_decoder(cls, midi_msg, data):
        index = data['index']

        status, b1, b2 = midi_msg
        if status in [0x90, 0x80]:
            y = b1 // 16
            x = b1 % 16

            if x == 8:
                return ['CC2', y + 8*index, b2]
            else:
                event = 'NoteOff' if status == 0x80 or b2 == 0 else 'NoteOn'
                return [event, x+8*index, y, b2]
        elif status in [0xb0]:
            x = b1 - 104
            return ['CC', x + 8*index, b2]

        return "???"

    def callback(self, msg, index):
        midi_msg, offset = msg

        message = self.callback_decoder(midi_msg, index)
        if message[0] == 'NoteOn':
            x, y = message[1:3]
            val = y*8 + x
            self.send_note_on(0, 0, val)

    def send_note_on(self, x, y, value):
        index = x//8
        self.launchpads[index].send_note_on(x-(index*8), y, value)

    def send_cc(self, button, value):
        index = button//8
        self.launchpads[index].send_cc(button-(index*8), value)

    def send_cc2(self, button, value):
        index = button//8
        self.launchpads[index].send_cc2(button-(index*8), value)

