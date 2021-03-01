#!/usr/bin/env python

import os, sys
basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
sys.path.append(lp)


from tkinter import *
from tkmacosx import Button
from app.dial import Dial

from miditool import torso_sequencer, notes
from rtmidi.midiutil import open_midiport

MODE_PATTERNS = 'patterns'
MODE_STEPS = 'steps'
MODE_PULSES = 'pulses'
MODE_ROTATE = 'rotate'
MODE_CYCLES = 'cycles'
MODE_DIVISION = 'division'
MODE_VELOCITY = 'velocity'
MODE_SUSTAIN = 'sustain'
MODE_PITCH = 'pitch'
MODE_HARMONY = 'harmony'
MODE_MUTE = 'mute'
MODE_REPEATS = 'repeats'
MODE_REPEATS_OFFSET = 'repeats_offset'
MODE_REPEATS_TIME = 'repeats_time'
MODE_REPEATS_PACE = 'repeats_pace'
MODE_PACE = 'pace'
MODE_VOICING = 'voicing'
MODE_MELODY = 'melody'
MODE_PHRASE = 'phrase'
MODE_ACCENT = 'accent'
MODE_ACCENT_CURVE = 'accent_curve'
MODE_STYLE = 'style'
MODE_SCALE = 'scale'
MODE_ROOT = 'root'
MODE_LENGTH = 'length'
MODE_QUANTIZE = 'quantize'
MODE_TIMING = 'timing'
MODE_DELAY = 'delay'
MODE_RANDOM = 'random'
MODE_RANDOM_RATE = 'random_rate'
MODE_TEMPO = 'tempo'

class App(Tk):
    colors = {
        'bg': '#333333',
        'active': '#bfd426',
        'active2': '#4cd426',
        'inactive': '#6b6b6b',
        'passive': '#26d4c0'
    }

    dials = [
        {
            'row': 0, 'col': 0, 'pos': 0, 'label': 'steps', 'alt_label': '', 'keybind': 'a',
            'dial_press_cmd': ['push_mode', [[MODE_STEPS]]], 'dial_release_cmd': ['pop_mode'],
            'property': 'steps',
            'min': 0, 'max': 16, 'type': int,
        },
        {
            'row': 0, 'col': 1, 'pos': 0, 'label': 'pulses', 'alt_label': 'rotate', 'keybind': 's',
            'dial_press_cmd': ['push_mode', [[MODE_PULSES, MODE_ROTATE]]], 'dial_release_cmd': ['pop_mode'],
            'property': 'pulses', 'alt_property': 'rotate',
            'min': 0, 'max': 16, 'type': int
        },
        {
            'row': 0, 'col': 2, 'pos': 0, 'label': 'cycles', 'alt_label': '', 'keybind': 'd',
            'dial_cmd': [], 'alt_dial_cmd': [],
        },
        {
            'row': 0, 'col': 3, 'pos': 0, 'label': 'division', 'alt_label': '', 'keybind': 'f',
            'dial_press_cmd': ['push_mode', [[MODE_DIVISION]]], 'dial_release_cmd': ['pop_mode'],
            'list': torso_sequencer.TorsoTrack.divisions,
        },
        {
            'row': 0, 'col': 4, 'pos': 0, 'label': 'velocity', 'alt_label': '', 'keybind': 'g',
            'dial_press_cmd': ['push_mode', [[MODE_VELOCITY]]], 'dial_release_cmd': ['pop_mode'],
            'alt_dial_cmd': [],
        },
        {
            'row': 0, 'col': 5, 'pos': 0, 'label': 'sustain', 'alt_label': '', 'keybind': 'h',
            'dial_press_cmd': ['push_mode', [[MODE_SUSTAIN]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'sustain', int, 0, 127],
            'alt_dial_cmd': [],
        },
        {
            'row': 0, 'col': 0, 'pos': 1, 'label': 'pitch', 'alt_label': 'harmony', 'keybind': 'j',
            'dial_press_cmd': ['push_mode', [[MODE_PITCH, MODE_HARMONY]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'pitch', int, -36, 36],
            'alt_dial_cmd': [],
        },
        {
            'row': 0, 'col': 1, 'pos': 1, 'label': 'length', 'alt_label': 'quantize', 'keybind': 'k',
            'dial_press_cmd': ['push_mode', [[MODE_LENGTH, MODE_QUANTIZE]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': [], 'alt_dial_cmd': [],
        },
        {
            'row': 0, 'col': 2, 'pos': 1, 'label': 'tempo', 'alt_label': '', 'keybind': 'l',
            'dial_press_cmd': ['push_mode', [[MODE_TEMPO]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'bpm', int, 50, 300],
            'alt_dial_cmd': [],
        },

        {
            'row': 1, 'col': 0, 'pos': 0, 'label': 'repeats', 'alt_label': 'offset', 'keybind': 'z',
            'dial_press_cmd': ['push_mode', [[MODE_REPEATS, MODE_REPEATS_OFFSET]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'repeats', int, 0, 4],
            'alt_dial_cmd': ['set_real_value', 'repeats_offset', float, 0, 1],
        },
        {
            'row': 1, 'col': 1, 'pos': 0, 'label': 'time', 'alt_label': 'pace', 'keybind': 'x',
            'dial_press_cmd': ['push_mode', [[MODE_REPEATS_TIME, MODE_REPEATS_PACE]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': [], 'alt_dial_cmd': [],
        },
        {
            'row': 1, 'col': 2, 'pos': 0, 'label': 'voicing', 'alt_label': 'style', 'keybind': 'c',
            'dial_press_cmd': ['push_mode', [[MODE_VOICING, MODE_STYLE]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'voicing', int, 0, 16],
            'alt_dial_cmd': ['set_real_value', 'style', int, 0, 1],
        },
        {
            'row': 1, 'col': 3, 'pos': 0, 'label': 'melody', 'alt_label': 'phrase', 'keybind': 'v',
            'dial_press_cmd': ['push_mode', [[MODE_MELODY, MODE_PHRASE]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'melody', float, 0, 1],
            'alt_dial_cmd': ['set_real_value', 'phrase', int, 0, 0],
        },
        {
            'row': 1, 'col': 4, 'pos': 0, 'label': 'accent', 'alt_label': 'curve', 'keybind': 'b',
            'dial_press_cmd': ['push_mode', [[MODE_ACCENT, MODE_ACCENT_CURVE]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'accent', float, 0, 1],
            'alt_dial_cmd': ['set_real_value', 'accent_curve', int, 0, 0],
        },
        {
            'row': 1, 'col': 5, 'pos': 0, 'label': 'timing', 'alt_label': 'delay', 'keybind': 'n',
            'dial_press_cmd': ['push_mode', [[MODE_TIMING, MODE_DELAY]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'timing', float, 0, 1],
            'alt_dial_cmd': ['set_real_value', 'delay', float, 0, 1],
        },
        {
            'row': 1, 'col': 0, 'pos': 1, 'label': 'scale', 'alt_label': 'root', 'keybind': 'm',
            'dial_press_cmd': ['push_mode', [[MODE_SCALE, MODE_ROOT]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': [], 'alt_dial_cmd': [],
        },
        {
            'row': 1, 'col': 1, 'pos': 1, 'label': 'midi ch', 'alt_label': '', 'keybind': ',',
            'dial_press_cmd': ['push_mode', [[MODE_SCALE, MODE_ROOT]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': ['set_real_value', 'channel', int, 0, 15],
            'alt_dial_cmd': [],
        },
        {
            'row': 1, 'col': 2, 'pos': 1, 'label': 'random', 'alt_label': 'rate', 'keybind': '.',
            'dial_press_cmd': ['push_mode', [[MODE_RANDOM, MODE_RANDOM_RATE]]], 'dial_release_cmd': ['pop_mode'],
            'dial_cmd': [], 'alt_dial_cmd': [],
        },
    ]
    buttons = [
        [
            [
                ['/1',       '',       '1', ],
                ['/2',       '',       '2', ],
                ['/4',       '',       '3', ],
                ['/8',       '',       '4', ],
                ['/16',      '',       '5', ],
                ['/32',      '',       '6', ],
                ['/64',      '',       '7', ],
                ['',         '',       '8', ],
            ],
            [
                ['',         'chrom',  'q', ],
                ['',         'major',  'w', ],
                ['/3',       'minor',  'e', ],
                ['/6',       'melo',   'r', ],
                ['/12',      'hex',    't', ],
                ['/24',      'aug',    'y', ],
                ['/48',      'penta',  'u', ],
                ['',         'user',   'i', ],
            ]
        ],
        [
            [
                ['play',     'stop',   '9',  ['play_pause', None]],
                [None,       None,     None],
                ['clear',    'copy',   '\-'],
                ['ctrl',     '',       '=', ['set_control', 'release_control']],
            ],
            [
                ['bank',    'save',    'p'],
                ['pattern', 'select',  '['],
                ['temp',    'multi',   ']'],
                ['mute',     '',       '\\', ['set_mute', 'release_mute']],
            ],
        ],
    ]

    def __init__(self):
        # super().__init__()

        midiout, port = open_midiport(
            None,
            "TORSO",
            use_virtual=True,
            client_name="TORSO"
        )

        self.button_pressed = {}
        self.dial_pressed = {}
        self.selected_track = None
        self.has_prev_key_release = {}

        self.old_modes = []
        self.mode = MODE_PATTERNS
        self.control = False
        self.pattern = None
        self.bank = 0
        self.active_patterns = {i: {} for i in range(16)}  # 16 banks

        self.rows = 2
        self.cols = 8
        self.w_buttons = [[], []]
        self.w_dials = [[], []]

        self.torso = torso_sequencer.TorsoSequencer(
            midiout=midiout,
            lookahead=0.02,
            bpm=120,
        )

        tp = torso_sequencer.TorsoTrack(
            notes=[('C', 4)],
            pulses=8,
            steps=16,
        )
        self.torso.add_track(track_name=(0, 0), track=tp)
        self.pattern = 0
        self.bank = 0

        # tp = torso_sequencer.TorsoTrack(
        #     notes=[
        #         ('C', 4),
        #         ('E', 4),
        #         ('G', 4),
        #         # ('B', 4)
        #     ],
        #     pulses=8,
        #     steps=16,
        #     repeats=2,
        #     # repeat_time=6,
        #     sustain=1,
        #     style=1,
        #     voicing=3,
        # )
        # self.torso.add_track(track_name='piano', track=tp)

        self.torso.pause()
        self.torso.start()

        Tk.__init__(self)
        self.title("boobs")

        self.configure(bg=self.colors['bg'])

        fl = Frame(self, border=10, bg=self.colors['bg'])
        fm = Frame(self, width=10, bg=self.colors['bg'])
        fr = Frame(self, border=10, bg=self.colors['bg'])
        fl.pack(side=LEFT, fill=X)
        fm.pack(side=LEFT, fill=NONE)
        fr.pack(side=LEFT, fill=X)

        flt = Frame(fl, bg=self.colors['bg'])
        flb = Frame(fl, bg=self.colors['bg'])
        flt.pack(side=TOP, fill=BOTH)
        flb.pack(side=TOP, fill=BOTH, pady=[50, 0])

        frt = Frame(fr, bg=self.colors['bg'])
        frb = Frame(fr, bg=self.colors['bg'])
        frt.pack(side=TOP, fill=BOTH)
        frb.pack(side=TOP, fill=BOTH, pady=[50, 0])

        frames = [flt, frt, flb, frb]

        for dial in self.dials:
            if 'property' in dial and 'dial_cmd' not in dial:
                dial['dial_cmd'] = ['set_real_value', dial['property'], dial['type'], dial['min'], dial['max']]

                if dial.get('alt_property'):
                    dial['alt_cmd'] = [
                        'set_real_value',
                        dial['alt_label'],
                        dial.get('type', dial.get('alt_type')),
                        dial.get('min', dial.get('alt_min')),
                        dial.get('max', dial.get('alt_max')),
                    ]

            f = Frame(frames[dial['pos']], bg=self.colors['bg'])
            f.grid(row=dial['row'], column=dial['col'])
            d = Dial(
                parent=f,
                command=lambda degrees, rowx=dial['row'], colx=dial['col'], bankx=dial['pos']: self.dial_callback(rowx, colx, bankx, degrees),
                zeroAxis='y',
                fill='#aaaaaa',
                press_command=self.make_callback(dial.get('dial_press_cmd')),
                release_command=self.make_callback(dial.get('dial_release_cmd')),
                label=dial['keybind'],
                bg=self.colors['bg'],
            )
            self.w_dials[dial['pos']].append(d)
            d.pack(side=TOP, fill=BOTH)
            lb = Label(f, text=dial['label'], bg=self.colors['bg'])
            lb.pack(side=TOP, fill=BOTH)
            lb = Label(f, text=dial['alt_label'], bg=self.colors['bg'])
            lb.pack(side=TOP, fill=BOTH)

            self.bind(
                f'<KeyPress-{dial["keybind"]}>',
                d.mid_press_cb,
            )

            self.bind(
                f'<KeyRelease-{dial["keybind"]}>',
                d.mid_release_cb,
            )

        for b, bank in enumerate(self.buttons):
            for r, row in enumerate(bank):
                for c, col in enumerate(row):
                    if col[0] is None:
                        continue

                    f = Frame(frames[b+2], bg=self.colors['bg'])
                    f.grid(row=r, column=c)
                    bt = Button(
                        f, height=70, width=70, text=col[2], bg=self.colors['inactive'], borderless=True,
                        activebackground=self.colors['inactive'],
                    )
                    self.w_buttons[b].append(bt)

                    self.bind(
                        f'<KeyPress-{col[2]}>',
                        lambda *args, rowx=r, colx=c, bankx=b, **kwargs: self.button_press_repeat(rowx, colx, bankx, *args, **kwargs)
                    )

                    self.bind(
                        f'<KeyRelease-{col[2]}>',
                        lambda *args, rowx=r, colx=c, bankx=b, **kwargs: self.button_release_repeat(rowx, colx, bankx, *args, **kwargs)
                    )

                    bt.bind(
                        '<ButtonPress>',
                        lambda *args, rowx=r, colx=c, bankx=b, **kwargs: self.button_press(rowx, colx, bankx, *args, **kwargs)
                    )
                    bt.bind(
                        '<ButtonRelease>',
                        lambda *args, rowx=r, colx=c, bankx=b, **kwargs: self.button_release(rowx, colx, bankx, *args, **kwargs)
                    )
                    bt.pack(side=TOP, fill=X)
                    lb = Label(f, text=col[0], bg=self.colors['bg'])
                    lb.pack(side=TOP, fill=X)
                    lb = Label(f, text=col[1], bg=self.colors['bg'])
                    lb.pack(side=TOP, fill=X)

        self.update_display()
        self.update_dials()

    def make_callback(self, args):
        if args is None:
            return None

        fn = getattr(self, args[0])

        if len(args) < 3:
            args.extend([None, None])
        elif len(args) < 2:
            args.append(None)

        a = args[1] or []
        kw = args[2] or {}
        return lambda: fn(*a, **kw)

    def push_mode(self, new_mode):
        if self.old_modes:
            return  # for now no mode stack, one mode at a time

        self.old_modes.append(self.mode)
        self.mode = new_mode
        self.update_display()

    def pop_mode(self):
        self.mode = self.old_modes.pop()
        self.update_display()

    def dial_press(self, *args, **kwargs):
        pass

    def dial_release(self, *args, **kwargs):
        pass

    def dial_callback(self, row, col, bank, degrees):
        print("dial", row, col, bank, degrees)
        dial = next(x for x in self.dials if bank == x['pos'] and row == x['row'] and col == x['col'])

        print(f"{row} {col} {bank} ctrl={self.control}-- {dial}")

        cmd = dial['alt_dial_cmd'] if self.control else dial['dial_cmd']

        print(f"cmd = {cmd}")

        if not cmd:
            return

        if cmd[0] == "set_real_value":
            if self.pattern is None or self.bank is None:
                print(f"need pattern or bank - bank={self.bank} pattern={self.pattern}")
                return
            track = self.torso.get_track((self.bank, self.pattern))
            field, ftype, fmin, fmax = cmd[1:]
            value = fmin + (fmax - fmin)*degrees/360.0
            if ftype is int:
                value = round(value)
            value = ftype(value)
            print(f"set {field}={value}")
            setattr(track, field, value)

            # FIXME make this into a proper pushing thing or context manager or something
            self.update_display()

    def button_command(self, row, col, bank, press=False):
        button = self.buttons[bank][row][col]
        if len(button) > 3:
            cmd = button[3][0 if press else 1]
        else:
            cmd = None

        return cmd if not cmd else getattr(self, cmd)

    def button_release_repeat(self, row, col, bank, event):
        bkey = (row, col, bank)
        self.has_prev_key_release[bkey] = self.after_idle(lambda: self.button_release(row, col, bank, event))

    def button_press_repeat(self, row, col, bank, event):
        bkey = (row, col, bank)

        hkr = self.has_prev_key_release.get(bkey)
        if hkr:
            self.after_cancel(hkr)
            self.has_prev_key_release[bkey] = None
        else:
            self.button_press(row, col, bank, event)

    def button_press(self, row, col, bank, event, *args, **kwargs):
        bkey = (row, col, bank)
        if bkey in self.button_pressed:
            return

        self.button_pressed[bkey] = 1

        print(f'press row={row} col={col} bank={bank} event={event} serial={event.serial}')

        if bank == 0:
            if self.mode == MODE_PATTERNS:
                self.pattern = row*self.cols + col
                self.update_dials()
            elif self.mode == MODE_MUTE:
                pattern = row*self.cols + col
                bank = self.active_patterns[self.bank]
                bank[pattern] = 'inactive' if bank.get(pattern) == 'active' else 'active'
        else:
            cmd = self.button_command(row, col, bank, press=True)
            if cmd:
                cmd()

        self.update_display()

    def button_release(self, row, col, bank, event, *args, **kwargs):
        bkey = (row, col, bank)

        self.has_prev_key_release[bkey] = None

        if bkey not in self.button_pressed:
            return

        self.button_pressed.pop(bkey)

        print(f'release row={row} col={col} bank={bank} event={event} serial={event.serial}')

        if bank == 0:
            pass
        else:
            cmd = self.button_command(row, col, bank, press=False)
            if cmd:
                cmd()

        self.update_display()

    def update_display(self):
        bank = self.active_patterns[self.bank]
        print(f"update display mode={self.mode}")

        if self.mode in [MODE_PATTERNS, MODE_MUTE]:
            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    if index == self.pattern:
                        color = 'active'
                    elif bank.get(index, None) in ['active']:
                        color = 'active2'
                    elif bank.get(index, None) in ['inactive']:
                        color = 'passive'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])

        elif self.mode in [MODE_STEPS]:
            track = self.torso.get_track((self.bank, self.pattern))
            value = track.steps

            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    if index <= value:
                        color = 'active2'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])
        elif self.mode in [MODE_PULSES]:
            track = self.torso.get_track((self.bank, self.pattern))
            seq = track.sequence
            print(seq)

            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    if index >= len(seq):
                        continue

                    if seq[index]:
                        color = 'active2'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])


        else:
            print(f"unknown mode {self.mode}")

        self.update(); self.update_idletasks()

    def update_dials(self):
        track = self.torso.get_track((self.bank, self.pattern))
        for dial in self.dials:
            prop = dial.get('alt_property' if self.control else 'property')
            if prop:
                index = self.cols*dial['row'] + dial['col']
                value = getattr(track, prop)
                a = min(359, 360*(value - dial['min']) / (dial['max'] - dial['min']))
                print("dial index", index, value, dial['max'] - dial['min'], a)
                w = self.w_dials[dial['pos']][index]
                w.set_angle(a, doCallback=False)

    def play_pause(self):
        print("play_pause")
        self.torso.play_pause()

    def set_control(self):
        self.control = True

    def release_control(self):
        self.control = False

    def set_mute(self):
        self.old_mode = self.mode
        self.mode = MODE_MUTE
        print(self.w_buttons[1])
        self.w_buttons[1][6].configure(bg=self.colors['active'])

    def release_mute(self):
        self.mode = self.old_mode
        self.w_buttons[1][6].configure(bg=self.colors['inactive'])


if __name__ == '__main__':
    app = App()
    app.mainloop()
    app.torso.join()
    app.midiout.close_port()
