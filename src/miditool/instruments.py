import copy
import logging
import time
from itertools import accumulate

import rtmidi
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROL_CHANGE

from .notes import note_to_number, number_to_note
from .scales import scales

logger = logging.getLogger(__name__)


class Instrument:
    def __init__(self, in_rule=None, out_rule=None, callback=None):
        self.midi_out = None
        logger.error("in_rule=%r, out_rule=%r", in_rule, out_rule)
        if in_rule:
            callback = callback or [self.input_callback, {}]

            midiin = rtmidi.MidiIn()
            label, index = in_rule
            matches = [x for x in enumerate(midiin.get_ports()) if label in x[1]]
            if matches:
                device = matches[index]
                self.midi_in = midiin.open_port(device[0], name=device[1])
                self.midi_in.set_callback(*callback)

        if out_rule:
            midiout = rtmidi.MidiOut()
            label, index = out_rule
            matches = [x for x in enumerate(midiout.get_ports()) if label in x[1]]
            if matches:
                logger.warning("out matches = %r", matches)
                device = matches[index]
                self.midi_out = midiout.open_port(device[0], name=device[1])

    @classmethod
    def input_callback(cls, msg, data):
        midi_message, offset = msg
        status, b1, b2 = midi_message
        print(f"{status:x} {b1} {b2} - {data}")

    def send_message(self, status, b1, b2):
        if not self.midi_out:
            return
        self.midi_out.send_message([status, b1, b2])


class Launchpad(Instrument):
    def __init__(self, index=0, callback=None):
        super().__init__(
            in_rule=["Launchpad", index],
            out_rule=["Launchpad", index],
            callback=callback,
        )
        self.index = index
        self.clear()
        self.lightshow()

        print(f"Launchpad {index} ready")

    def lightshow(self):
        d = .08
        for i in range(11):
            if i > 2:
                self.send_note_on(i-3, i-3, 0)
                self.send_note_on(7 - i + 3, i-3, 0)

            if i < 8:
                self.send_note_on(i, i, 20)
                self.send_note_on(7-i, i, 20)

            time.sleep(d)

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
        self.send_message(NOTE_ON, y*16+x, value)

    def send_note_off(self, x, y, value):
        self.send_message(NOTE_OFF, y*16+x, value)

    def send_cc(self, button, value):
        self.send_message(CONTROL_CHANGE, 104+button, value)

    def send_cc2(self, button, value):
        self.send_note_on(8, button, value)


class StatefulLaunchpad(Launchpad):
    def __init__(self, index=0, callback=None):
        super().__init__(index=index, callback=callback)
        self.state = []
        for y in range(8):
            this = []
            for x in range(8):
                this.append(0)

            self.state.append(this)

        self.display_state = copy.deepcopy(self.state)

    def set_state(self, x, y, value):
        self.state[x][y] = value

    def update(self):
        for x in range(8):
            for y in range(8):
                val = self.state[x][y]
                if val != self.display_state[x][y]:
                    self.send_note_on(x, y, val)

        self.display_state = copy.deepcopy(self.state)


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
        # print(self.off_map)
        # print(self.scale_map)

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

    def send_note_off(self, x, y, value):
        index = x//8
        self.launchpads[index].send_note_off(x-(index*8), y, value)

    def send_cc(self, button, value):
        index = button//8
        self.launchpads[index].send_cc(button-(index*8), value)

    def send_cc2(self, button, value):
        index = button//8
        self.launchpads[index].send_cc2(button-(index*8), value)

    def clear(self):
        for l in self.launchpads:
            l.clear()