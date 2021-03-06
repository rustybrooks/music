#!/usr/bin/env python

import os, sys
import json

basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
sys.path.append(lp)


from tkinter import *
from tkmacosx import Button
import platform
from miditool import torso_sequencer, notes
from rtmidi.midiutil import open_midiport

from app.dial import Dial


MODE_TRACKS = 'tracks'
MODE_PATTERNS = 'patterns'
MODE_SAVE = 'save'
MODE_BANKS = 'banks'
MODE_SELECT = 'select'
MODE_TEMP = 'temp'
MODE_MULTI = 'multi'
MODE_CLEAR = 'clear'
MODE_COPY = 'copy'

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
        'bg':             '#333333',
        'active':         '#bfd426',
        'active2':        '#4cd426',
        'inactive':       '#6b6b6b',
        'passive':        '#26d4c0',
        'white_active':   '#ffdddd',
        'white_inactive': '#bbbbbb',
        'black_active':   '#997777',
        'black_inactive': '#444444',
    }

    dials = [
        {
            'row': 0, 'col': 0, 'pos': 0, 'label': 'steps', 'alt_label': '', 'keybind': 'a',
            'property': 'steps', 'min': 1, 'max': 16, 'type': int,
            'mode': MODE_STEPS,
        },
        {
            'row': 0, 'col': 1, 'pos': 0, 'label': 'pulses', 'alt_label': 'rotate', 'keybind': 's',
            'mode': MODE_PULSES, 'property': 'pulses', 'min': 1, 'max': 16, 'type': int,
            'alt_mode': MODE_ROTATE, 'alt_property': 'rotate', 'alt_min': 0, 'alt_max': 15,
        },
        {
            'row': 0, 'col': 2, 'pos': 0, 'label': 'cycles', 'alt_label': '', 'keybind': 'd',
        },
        {
            'row': 0, 'col': 3, 'pos': 0, 'label': 'division', 'alt_label': '', 'keybind': 'f',
            'mode': MODE_DIVISION, 'property': 'division', 'list': torso_sequencer.TorsoTrack.divisions,
        },
        {
            'row': 0, 'col': 4, 'pos': 0, 'label': 'velocity', 'alt_label': '', 'keybind': 'g',
            'mode': MODE_VELOCITY, 'property': 'velocity', 'min': 0, 'max': 127, 'type': int,
        },
        {
            'row': 0, 'col': 5, 'pos': 0, 'label': 'sustain', 'alt_label': '', 'keybind': 'h',
            'mode': MODE_SUSTAIN, 'property': 'sustain', 'min': 0, 'max': 1, 'type': float,
        },
        {
            'row': 0, 'col': 0, 'pos': 1, 'label': 'pitch', 'alt_label': 'harmony', 'keybind': 'j',
            'mode': MODE_PITCH, 'property': 'pitch', 'min': -36, 'max': 36, 'type': int,
            'alt_mode': MODE_HARMONY, 'alt_property': 'harmony',  # FIXME min/max etc?
        },
        {
            'row': 0, 'col': 1, 'pos': 1, 'keybind': 'k',
            'mode': MODE_LENGTH, 'label': 'length',
            'alt_mode': MODE_QUANTIZE, 'alt_label': 'quantize',
        },
        {
            'row': 0, 'col': 2, 'pos': 1, 'label': 'tempo', 'alt_label': '', 'keybind': 'l',
            'mode': MODE_TEMPO, 'property': 'bpm', 'min': 50, 'max': 300, 'type': int,
        },
        {
            'row': 1, 'col': 0, 'pos': 0, 'label': 'repeats', 'alt_label': 'offset', 'keybind': 'z',
            'mode': MODE_REPEATS, 'property': 'repeats', 'min': 0, 'max': 15, 'type': int,
            'alt_mode': MODE_REPEAT_OFFSET, 'alt_property': 'repeat_offset', 'alt_min': 0, 'alt_max': 15, 'alt_type': int,
        },
        {
            'row': 1, 'col': 1, 'pos': 0, 'label': 'time', 'alt_label': 'pace', 'keybind': 'x',
            'mode': MODE_REPEAT_TIME, 'property': 'repeat_time', 'list': torso_sequencer.TorsoTrack.divisions,
            'alt_mode': MODE_REPEAT_PACE,
        },
        {
            'row': 1, 'col': 2, 'pos': 0, 'label': 'voicing', 'alt_label': 'style', 'keybind': 'c',
            'mode': MODE_VOICING, 'property': 'voicing', 'min': 0, 'max': 15, 'type': int,
            'alt_mode': MODE_STYLE, 'alt_property': 'style', 'alt_list': torso_sequencer.TorsoTrack.styles,

        },
        {
            'row': 1, 'col': 3, 'pos': 0, 'label': 'melody', 'alt_label': 'phrase', 'keybind': 'v',
            'mode': MODE_MELODY, 'property': 'melody', 'min': 0, 'max': 1, 'type': float,
            'alt_mode': MODE_PHRASE, 'alt_property': 'phrase', 'alt_list': torso_sequencer.TorsoTrack.phrases,
        },
        {
            'row': 1, 'col': 4, 'pos': 0, 'label': 'accent', 'alt_label': 'curve', 'keybind': 'b',
            'mode': MODE_ACCENT,  'property': 'accent', 'min': 0, 'max': 1, 'type': float,
            'alt_mode': MODE_ACCENT_CURVE, 'alt_property': 'accent_curve', 'alt_list': torso_sequencer.TorsoTrack.accent_curves,
        },
        {
            'row': 1, 'col': 5, 'pos': 0, 'label': 'timing', 'alt_label': 'delay', 'keybind': 'n',
            'mode': MODE_TIMING, 'property': 'timing', 'min': 0, 'max': 1, 'type': float,
            'alt_mode': MODE_DELAY, 'alt_property': 'delay',
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
            # 'mode': MODE_RANDOM, 'property': 'random', 'min': 0, 'max': 1, 'type': float,  # this is gonna be special
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
                ['clear',    'copy',   '\-', ['set_clear', 'release_mode']],
                ['ctrl',     '',       '=', ['set_control', 'release_control']],
            ],
            [
                ['bank',    'save',    'p',  ['set_bank', 'release_mode']],
                ['pattern', 'select',  '[',  ['set_pattern', 'release_mode']],
                ['temp',    'multi',   ']',  ],
                ['mute',     '',       '\\', ['set_mute', 'release_mode']],
            ],
        ],
    ]

    def __init__(self, bank_file):
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
        self.mode = MODE_TRACKS
        self.control = False
        self.track = 0
        self.pattern = 0
        self.bank = 0
        self.pitch_octave = 3

        self.rows = 2
        self.cols = 8
        self.w_buttons = [[], []]
        self.w_dials = [[], []]

        with open(bank_file) as f:
            data = json.load(f)

        targs = {
            'midiout': midiout
        }
        tracks = data.pop('tracks', [])
        targs.update(**data)
        self.torso = torso_sequencer.TorsoSequencer(**targs)

        for i, track in enumerate(tracks):
            bank = track.get('bank', 0)
            pattern = track.get('pattern', 0)
            trackn = track.get('track', i)
            track['slices'] = [torso_sequencer.TrackSlice(**s) for s in track.pop('slices', [])]
            t = torso_sequencer.TorsoTrack(**track)
            self.torso.add_track(track_name=(bank, pattern, trackn), track=t)

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

        self.bind("<KeyPress-Control_L>", self.set_control)
        self.bind("<KeyRelease-Control_L>", self.release_control)

        for dial in self.dials:

            dial_press_cmd = None
            dial_release_cmd = None

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
                d.mid_press_cb_repeat,
            )

            self.bind(
                f'<KeyRelease-{dial["keybind"]}>',
                d.mid_release_cb_repeat,
            )

        for b, bank in enumerate(self.buttons):
            for r, row in enumerate(bank):
                for c, col in enumerate(row):
                    if col[0] is None:
                        continue

                    f = Frame(frames[b+2], bg=self.colors['bg'])
                    f.grid(row=r, column=c)
                    kwargs = {}
                    if platform.system in ['Darwin']:
                        kwargs = {'activebackground': self.colors['inactive']}
                    bt = Button(
                        f, height=70, width=70, text=col[2], bg=self.colors['inactive'], borderless=True,
                        **kwargs
                    )
                    self.w_buttons[b].append(bt)

                    key = col[2]
                    if key == '\\':
                        key = "backslash"
                    self.bind(
                        f'<KeyPress-{key}>',
                        lambda *args, rowx=r, colx=c, bankx=b, **kwargs: self.button_press_repeat(rowx, colx, bankx, *args, **kwargs)
                    )

                    self.bind(
                        f'<KeyRelease-{key}>',
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

    def dial_callback(self, degrees):
        if self.pattern is None or self.bank is None or self.track is None:
            print(f"need pattern or bank - bank={self.bank} pattern={self.pattern} track={self.track}")
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

        # print(f'press row={row} col={col} bank={bank} event={event} serial={event.serial}')

        index = row*self.cols + col
        if bank == 0:
            if self.mode == MODE_TRACKS:
                self.track = row*self.cols + col
                self.update_dials()
            elif self.mode == MODE_PATTERNS:
                self.pattern = row*self.cols + col
                self.update_dials()
            elif self.mode == MODE_BANKS:
                self.bank = row*self.cols + col
                self.update_dials()
            elif self.mode == MODE_MUTE:
                track = self.torso.get_track((self.bank, self.pattern, row*self.cols + col))
                track.muted = not track.muted
            elif self.mode in [MODE_PITCH]:
                pass
            elif self.mode in [
                MODE_CHANNEL, MODE_ACCENT_CURVE, MODE_MELODY, MODE_PHRASE, MODE_STYLE,
            ]:
                if self.pattern is None or self.bank is None or self.track is None:
                    print(f"need pattern or bank - bank={self.bank} pattern={self.pattern} track={self.track}")
                    return

                self.set_value(index)
                self.update_display()

            elif self.mode in [
                MODE_STEPS, MODE_PULSES, MODE_ROTATE, MODE_REPEATS, MODE_REPEAT_OFFSET, MODE_VOICING,
                MODE_VELOCITY, MODE_SUSTAIN, MODE_PITCH, MODE_REPEAT_PACE, MODE_MELODY, MODE_PHRASE, MODE_ACCENT,
                MODE_ACCENT_CURVE, MODE_STYLE, MODE_ROOT, MODE_TIMING, MODE_DELAY, MODE_TEMPO, MODE_CHANNEL,
            ]:
                if self.pattern is None or self.bank is None or self.track is None:
                    print(f"need pattern or bank - bank={self.bank} pattern={self.pattern} track={self.track}")
                    return

                self.set_value(index, interpolate=16)
                self.update_display()

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

        # print(f'release row={row} col={col} bank={bank} event={event} serial={event.serial}')

        if bank == 0:
            pass
        else:
            cmd = self.button_command(row, col, bank, press=False)
            if cmd:
                cmd()

        self.update_display()

    def get_value(self, dial=None, interpolate=None, asint=False, asindex=True):
        track = self.torso.get_track((self.bank, self.pattern, self.track))
        dial = dial or self.dial_map.get(self.mode)

        if not dial:
            print(f"No dial map for mode={self.mode}")
            return None

        if self.control and 'alt_property' not in dial:
            print(f"No alt property for mode={self.mode}")
            return None

        value = getattr(track, dial['alt_property' if self.control else 'property'])

        lval = dial.get('alt_list' if self.control else 'list')
        if asindex and lval is not None:
           value = lval.index(value)

        print(f"get_value... lval={lval} value={value}")

        if interpolate is not None:
            value = interpolate*(value - dial['min']) / (dial['max'] - dial['min'])

        if asint:
            value = int(value)

        return value

    def set_value(self, value, interpolate=None):
        track = self.torso.get_track((self.bank, self.pattern, self.track))
        dial = self.dial_map.get(self.mode)
        if not dial:
            print(f"No dial map for mode={self.mode}")
            return None

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
            fmax = len(dial['alt_list']) - 1
            ftype = int
            lval = dial['alt_list']
        else:
            if self.control:
                fmin, fmax, ftype = dial.get('alt_min', dial['min']), dial.get('alt_max', dial['max']), dial.get('alt_type', dial['type'])
            else:
                fmin, fmax, ftype = dial['min'], dial['max'], dial['type']

        if interpolate:
            value = fmin + (fmax - fmin)*value/interpolate
            if ftype is int:
                value = round(value)

            value = ftype(value)

        if lval:
            print(f"setattr prop={prop} value={lval[value]}")
            setattr(track, prop, lval[value])
        else:
            print(f"setattr prop={prop} value={value}")
            setattr(track, prop, value)

    def update_display(self):
        for b, bank in enumerate(self.buttons):
            if b != 0:
                continue

            for r, row in enumerate(bank):
                for c, col in enumerate(row):
                    index = r*self.cols + c
                    self.w_buttons[0][index].configure(text=col[2])

        self.w_buttons[1][0].configure(
            bg=self.colors['active' if not self.torso._paused else 'inactive'],
        )
        self.w_buttons[1][1].configure(
            bg=self.colors['active' if self.mode in [MODE_CLEAR, MODE_COPY] else 'inactive'],
        )
        self.w_buttons[1][2].configure(
            bg=self.colors['active' if self.control else 'inactive'],
        )
        self.w_buttons[1][3].configure(
            bg=self.colors['active' if self.mode in [MODE_BANKS, MODE_SELECT] else 'inactive'],
        )
        self.w_buttons[1][4].configure(
            bg=self.colors['active' if self.mode in [MODE_PATTERNS, MODE_SAVE] else 'inactive'],
        )
        self.w_buttons[1][4].configure(
            bg=self.colors['active' if self.mode in [MODE_TEMP, MODE_MULTI] else 'inactive'],
        )
        self.w_buttons[1][6].configure(
            bg=self.colors['active' if self.mode in [MODE_MUTE] else 'inactive'],
        )

        if self.mode in [MODE_TRACKS, MODE_MUTE]:
            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    track = self.torso.get_track((self.bank, self.pattern, index), create=False)
                    if index == self.track:
                        color = 'active'
                    elif track and not track.muted:
                        color = 'active2'
                    elif track and track.muted:
                        color = 'passive'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])
        elif self.mode in [MODE_PATTERNS]:
            pass
        elif self.mode in [MODE_BANKS]:
            pass
        elif self.mode in [
            MODE_STEPS, MODE_VELOCITY, MODE_SUSTAIN, MODE_REPEATS, MODE_REPEAT_OFFSET,
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
            MODE_CHANNEL, MODE_ACCENT_CURVE, MODE_MELODY, MODE_PHRASE, MODE_STYLE,
        ]:
            value_index = self.get_value(asint=True)

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
            dmap = {
                1: [0, 0],
                2: [0, 1],
                4: [0, 2],
                8: [0, 3],
                16: [0, 4],
                32: [0, 5],
                64: [0, 6],
                3: [1, 2],
                6: [1, 3],
                12: [1, 4],
                24: [1, 5],
                48: [1, 6],
            }

            value = self.get_value(asindex=False)
            r, c = dmap[value]

            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col

                    if row == r and col == c:
                        color = 'active2'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])

        elif self.mode in [MODE_PULSES, MODE_ROTATE]:
            track = self.torso.get_track((self.bank, self.pattern, self.track))
            seq = track.sequence

            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    if index >= len(seq):
                        continue

                    if seq[(index - track.rotate) % len(seq)]:
                        color = 'active2'
                    else:
                        color = 'inactive'

                    self.w_buttons[0][index].configure(bg=self.colors[color])
        elif self.mode in [MODE_PITCH]:
            for row in range(2):
                for col in range(8):
                    index = row*self.cols + col
                    self.w_buttons[0][index].configure(bg=self.colors['inactive'])

            track = self.torso.get_track((self.bank, self.pattern, self.track))
            our_notes = [notes.number_to_note(x)[0] for x in track.notes]
            # white keys
            for i, n in zip(range(8), ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'UP']):
                row = 1
                col = i
                index = row*self.cols + col
                self.w_buttons[0][index].configure(
                    bg=self.colors['white_active' if n in our_notes else 'white_inactive'],
                    text=f"{n}{self.pitch_octave if n and n not in ['UP', 'DN'] else ''}",
                )

            # black keys
            for i, n in zip(range(8), ['', 'C#', 'D#', '', 'F#', 'G#', 'A#', 'DN']):
                row = 0
                col = i
                index = row*self.cols + col
                self.w_buttons[0][index].configure(
                    bg=self.colors['black_active' if n in our_notes else 'black_inactive'],
                    text=f"{n}{self.pitch_octave if n and n not in ['UP', 'DN'] else ''}",
                )
        else:
            print(f"unknown mode {self.mode}")

        self.update(); self.update_idletasks()

    def update_dials(self):
        for dial in self.dials:
            prop = dial.get('alt_property' if self.control else 'property')
            list_key = 'alt_list' if self.control else 'list'
            if prop:
                c = 6 if dial['pos'] == 0 else 3
                index = c*dial['row'] + dial['col']
                value = self.get_value(dial=dial)
                if list_key in dial:
                    # value = dial['list'].index(value)
                    dmin = 0
                    dmax = len(dial[list_key])
                else:
                    dmin = dial.get('alt_min' if self.control else 'min', dial['min'])
                    dmax = dial.get('alt_max' if self.control else 'max', dial['max'])

                # print(f"prop={prop} val={value} min={dmin} max={dmax}")
                a = min(359, 360*(value - dmin) / (dmax - dmin))
                w = self.w_dials[dial['pos']][index]
                w.set_angle(a, doCallback=False)

    def play_pause(self):
        self.torso.play_pause()

    def set_control(self, *args, **kwargs):
        # print("ctrl on")
        self.control = True
        self.update_dials()

    def release_control(self, *args, **kwargs):
        # print("ctrl off")
        self.control = False
        self.update_dials()

    def release_mode(self):
        self.pop_mode()

    def set_temp(self):
        self.push_mode([MODE_TEMP, MODE_MULTI])

    def set_mute(self):
        self.push_mode([MODE_MUTE, None])

    def set_bank(self):
        self.push_mode([MODE_BANKS, MODE_SAVE])

    def set_pattern(self):
        self.push_mode([MODE_PATTERNS, MODE_SELECT])

    def set_clear(self):
        self.push_mode([MODE_CLEAR, MODE_COPY])

if __name__ == '__main__':
    app = App(sys.argv[1])
    app.mainloop()
    app.torso.join()
    app.midiout.close_port()
