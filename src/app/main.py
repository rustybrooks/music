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
MODE_REPEAT_OFFSET = 'repeat_offset'
MODE_REPEAT_TIME = 'repeat_time'
MODE_REPEAT_PACE = 'repeat_pace'
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
MODE_CHANNEL = 'channel'


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
            'property': 'steps', 'min': 1, 'max': 16, 'type': int,
            'mode': MODE_STEPS,
        },
        {
            'row': 0, 'col': 1, 'pos': 0, 'label': 'pulses', 'alt_label': 'rotate', 'keybind': 's',
            'property': 'pulses', 'alt_property': 'rotate', 'min': 0, 'max': 16, 'type': int,
            'mode': MODE_PULSES, 'alt_mode': MODE_ROTATE,
        },
        {
            'row': 0, 'col': 2, 'pos': 0, 'label': 'cycles', 'alt_label': '', 'keybind': 'd',
        },
        {
            'row': 0, 'col': 3, 'pos': 0, 'label': 'division', 'alt_label': '', 'keybind': 'f',
            'property': 'division',
            'list': torso_sequencer.TorsoTrack.divisions,
            'mode': MODE_DIVISION,
        },
        {
            'row': 0, 'col': 4, 'pos': 0, 'label': 'velocity', 'alt_label': '', 'keybind': 'g',
            'property': 'velocity', 'min': 0, 'max': 127, 'type': int,
            'mode': MODE_VELOCITY,
        },
        {
            'row': 0, 'col': 5, 'pos': 0, 'label': 'sustain', 'alt_label': '', 'keybind': 'h',
            'property': 'sustain', 'min': 0, 'max': 1, 'type': float,
            'mode': MODE_SUSTAIN,
        },
        {
            'row': 0, 'col': 0, 'pos': 1, 'label': 'pitch', 'alt_label': 'harmony', 'keybind': 'j',
            'property': 'pitch', 'min': -36, 'max': 36, 'type': int,
            'alt_property': 'harmony',  # FIXME min/max etc?
            'mode': MODE_PITCH, 'alt_mode': MODE_HARMONY,
        },
        {
            'row': 0, 'col': 1, 'pos': 1, 'label': 'length', 'alt_label': 'quantize', 'keybind': 'k',
            'mode': MODE_LENGTH, 'alt_mode': MODE_QUANTIZE,
        },
        {
            'row': 0, 'col': 2, 'pos': 1, 'label': 'tempo', 'alt_label': '', 'keybind': 'l',
            'property': 'bpm', 'min': 50, 'max': 300, 'type': int,
            'mode': MODE_TEMPO,
        },
        {
            'row': 1, 'col': 0, 'pos': 0, 'label': 'repeats', 'alt_label': 'offset', 'keybind': 'z',
            'property': 'repeats', 'min': 0, 'max': 15, 'type': int,
            'alt_property': 'repeat_offset', 'alt_min': 0, 'alt_max': 15, 'alt_type': int,
            'mode': MODE_REPEATS, 'alt_mode': MODE_REPEAT_OFFSET,
        },
        {
            'row': 1, 'col': 1, 'pos': 0, 'label': 'time', 'alt_label': 'pace', 'keybind': 'x',
            'mode': MODE_REPEAT_TIME, 'alt_mode': MODE_REPEAT_PACE,
            'property': 'repeat_time', 'list': torso_sequencer.TorsoTrack.divisions,
        },
        {
            'row': 1, 'col': 2, 'pos': 0, 'label': 'voicing', 'alt_label': 'style', 'keybind': 'c',
            'property': 'voicing', 'min': 0, 'max': 15, 'type': int,
            'alt_property': 'style', 'alt_list': torso_sequencer.TorsoTrack.styles,
            'mode': MODE_VOICING, 'alt_mode': MODE_STYLE,
        },
        {
            'row': 1, 'col': 3, 'pos': 0, 'label': 'melody', 'alt_label': 'phrase', 'keybind': 'v',
            'mode': MODE_MELODY, 'property': 'melody', 'min': 0, 'max': 1, 'type': float,
            'alt_mode': MODE_PHRASE, 'alt_property': 'phrase', 'alt_list': torso_sequencer.TorsoTrack.phrases,

        },
        {
            'row': 1, 'col': 4, 'pos': 0, 'label': 'accent', 'alt_label': 'curve', 'keybind': 'b',
            'property': 'accent', 'min': 0, 'max': 1, 'type': float,
            'alt_property': 'accent_curve', 'alt_list': torso_sequencer.TorsoTrack.accent_curves,
            'mode': MODE_ACCENT, 'alt_mode': MODE_ACCENT_CURVE,
        },
        {
            'row': 1, 'col': 5, 'pos': 0, 'label': 'timing', 'alt_label': 'delay', 'keybind': 'n',
            'property': 'timing', 'min': 0, 'max': 1, 'type': float,
            'alt_property': 'delay',
            'mode': MODE_TIMING, 'alt_mode': MODE_DELAY,
        },
        {
            'row': 1, 'col': 0, 'pos': 1, 'label': 'scale', 'alt_label': 'root', 'keybind': 'm',
            'mode': MODE_SCALE, 'list': torso_sequencer.TorsoTrack.scales,
            'alt_mode': MODE_ROOT,  # FIXME pick from notes available?
        },
        {
            'row': 1, 'col': 1, 'pos': 1, 'label': 'midi ch', 'alt_label': '', 'keybind': ',',
            'mode': MODE_CHANNEL, 'property': 'channel', 'min': 0, 'max': 16, 'type': int,
        },
        {
            'row': 1, 'col': 2, 'pos': 1, 'label': 'random', 'alt_label': 'rate', 'keybind': '.',
            # 'mode': MODE_RANDOM, 'property': 'random', 'min': 0, 'max': 16, 'type': int,  # this is gonna be special
            'alt_mode': MODE_RANDOM_RATE, 'alt_list': torso_sequencer.TorsoTrack.divisions,
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
            client_name="TORSO",
            port_name="TORSO"
        )

        self.dial_map = {}
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
            notes=[('D', 4)],
            pulses=8,
            steps=16,
        )
        self.torso.add_track(track_name=(0, 0), track=tp)
        self.pattern = 0
        self.bank = 0

        tp2 = torso_sequencer.TorsoTrack(
            notes=[
                ('C', 4),
                ('E', 4),
                ('G', 4),
                # ('B', 4)
            ],
            pulses=8,
            steps=16,
            repeats=2,
            # repeat_time=6,
            sustain=1,
            style=1,
            voicing=3,
        )
        self.torso.add_track(track_name=(0, 1), track=tp2)

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

            dial_press_cmd = None
            dial_release_cmd = None
            dial_cmd = None

            if 'mode' in dial:
                dial_press_cmd = lambda _m=[dial['mode'], dial.get('alt_mode')]: self.push_mode(_m)
                dial_release_cmd = self.pop_mode
                self.dial_map[dial['mode']] = dial
                if 'alt_mode' in dial:
                    self.dial_map[dial['alt_mode']] = dial

            f = Frame(frames[dial['pos']], bg=self.colors['bg'])
            f.grid(row=dial['row'], column=dial['col'])
            d = Dial(
                parent=f,
                command=self.dial_callback,
                zeroAxis='y',
                fill='#aaaaaa',
                press_command=dial_press_cmd,
                release_command=dial_release_cmd,
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

    def push_mode(self, new_mode):
        if self.old_modes:
            return  # for now no mode stack, one mode at a time

        if self.control:
            mode = new_mode[1] if len(new_mode) > 1 else None
        else:
            mode = new_mode[0]

        if not mode:
            return

        self.old_modes.append(self.mode)
        self.mode = mode
        self.update_display()

    def pop_mode(self):
        self.mode = self.old_modes.pop()
        self.update_display()

    def dial_press(self, *args, **kwargs):
        pass

    def dial_release(self, *args, **kwargs):
        pass

    def dial_callback(self, degrees):
        if self.pattern is None or self.bank is None:
            print(f"need pattern or bank - bank={self.bank} pattern={self.pattern}")
            return

        self.set_value(degrees, interpolate=360)
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

    def get_value(self, interpolate=None, asint=False):
        track = self.torso.get_track((self.bank, self.pattern))
        dial = self.dial_map.get(self.mode)

        if not dial:
            print(f"No dial map for mode={self.mode}")

        if self.control and 'alt_property' not in dial:
            print(f"No alt property for mode={self.mode}")
            return None

        value = getattr(track, dial['alt_property' if self.control else 'property'])

        if interpolate is not None:
            value = interpolate*(value - dial['min']) / (dial['max'] - dial['min'])

        if asint:
            value = int(value)

        return value

    def set_value(self, value, interpolate=None):
        track = self.torso.get_track((self.bank, self.pattern))
        dial = self.dial_map[self.mode]
        prop = dial.get('alt_property' if self.control else 'property')
        if not prop:
            print(f"set_value - mode={self.mode} no property")
            return

        lval = None
        if not self.control and 'list' in dial:
            fmin = 0
            fmax = len(dial['list']) - 1
            ftype = int
            lval = dial['list']
        elif self.control and 'alt_list' in dial:
            fmin = 0
            fmax = len(dial['list']) - 1
            ftype = int
            lval = dial['alt_list']
        else:
            if self.control:
                fmin, fmax, ftype = dial.get('alt_min', dial['min']), dial.get('alt_max', dial['max']), dial.get('alt_type', dial['type'])
            else:
                fmin, fmax, ftype = dial['min'], dial['max'], dial['type']

        if interpolate:
            value = fmin + (fmax - fmin)*value/360.0
            if ftype is int:
                value = round(value)

            value = ftype(value)

        print(f"setattr prop={prop} value={value}")
        if lval:
            setattr(track, prop, lval[value])
        else:
            setattr(track, prop, value)

    def update_display(self):
        bank = self.active_patterns[self.bank]

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

        elif self.mode in [
            MODE_STEPS, MODE_ROTATE, MODE_VELOCITY, MODE_SUSTAIN, MODE_PITCH, MODE_REPEATS, MODE_REPEAT_OFFSET,
            MODE_ACCENT, MODE_LENGTH, MODE_TIMING, MODE_DELAY, MODE_RANDOM, MODE_RANDOM_RATE, MODE_TEMPO,
            MODE_VOICING
        ]:  # show all buttons from 0 to value
            value_index = self.get_value(interpolate=16, asint=True)

            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    if index <= value_index:
                        color = 'active2'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])
        elif self.mode in [
            MODE_CHANNEL, MODE_ACCENT_CURVE, MODE_MELODY
        ]:
            value_index = self.get_value(interpolate=16, asint=True)

            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    if index == value_index:
                        color = 'active2'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])

        elif self.mode in [
            MODE_DIVISION, MODE_REPEAT_TIME
        ]:
            pass  # figure this shit out
        elif self.mode in [MODE_PULSES]:
            track = self.torso.get_track((self.bank, self.pattern))
            seq = track.sequence

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
                c = 6 if dial['pos'] == 0 else 3
                index = c*dial['row'] + dial['col']
                value = getattr(track, prop)
                print("prop...", prop, index, dial['pos'], len(self.w_dials[dial['pos']]))
                if 'list' in dial:
                    value = dial['list'].index(value)
                    dmin = 0
                    dmax = len(dial['list']) - 1
                else:
                    dmin = dial['min']
                    dmax = dial['max']

                a = min(359, 360*(value - dmin) / (dmax - dmin))
                w = self.w_dials[dial['pos']][index]
                w.set_angle(a, doCallback=False)

    def play_pause(self):
        self.torso.play_pause()

    def set_control(self):
        self.control = True

    def release_control(self):
        self.control = False

    def set_mute(self):
        self.old_mode = self.mode
        self.mode = MODE_MUTE
        self.w_buttons[1][6].configure(bg=self.colors['active'])

    def release_mute(self):
        self.mode = self.old_mode
        self.w_buttons[1][6].configure(bg=self.colors['inactive'])


if __name__ == '__main__':
    app = App()
    app.mainloop()
    app.torso.join()
    app.midiout.close_port()
