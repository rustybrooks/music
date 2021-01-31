import copy
import rtmidi


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
            print(f"callback set to {callback}")

        if out_rule:
            midiout = rtmidi.MidiOut()
            label, index = out_rule
            matches = [x for x in enumerate(midiout.get_ports()) if label in x[1]]
            device = matches[index]
            self.midi_out = midiout.open_port(device[0], name=device[1])

    def input_callback(self, msg, data):
        midi_message, offset = msg
        status, b1, b2 = midi_message

        print(f"{status:x} {b1} {b2}")

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

        for i in range(9):
            self.send_cc(i, 0)

        for x in range(10):
            for y in range(9):
                self.send_note_on(x, y, 0)

        print(f"Launchpad {index} ready")

    def send_note_on(self, x, y, value):
        self.send_message(0x90, y*16+x, value)

    def send_cc(self, button, value):
        self.send_message(0xb0, 104+button, value)

    def send_cc2(self, button, value):
        print(f"{self.index} {button} {value}")
        self.send_note_on(8, button, value)


class MultiLaunchpad:
    def __init__(self, number=2, callback_data=None):
        if callback_data is None:
            callback_data = [{} for i in range(number)]
        if not isinstance(callback_data, (list, tuple)):
            callback_data = [copy.deepcopy(callback_data) for i in range(number)]

        for i, d in enumerate(callback_data):
            d.update({'index': i})

        print(callback_data)

        self.launchpads = [
            Launchpad(
                index=i,
                callback=[self.callback, callback_data[i]]
            ) for i in range(number)
        ]

    def callback_decoder(self, midi_msg, data):
        index = data['index']

        status, b1, b2 = midi_msg
        print(status, b1, b2)
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
        print(self.callback_decoder(midi_msg, index))

    def send_note_on(self, x, y, value):
        index = x//8
        self.launchpads[index].send_note_on(x-(index*8), y, value)

    def send_cc(self, button, value):
        index = button//8
        self.launchpads[index].send_cc(button-(index*8), value)

    def send_cc2(self, button, value):
        index = button//8
        self.launchpads[index].send_cc2(button-(index*8), value)
