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
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

MODE_PATTERNS = 'patterns'
MODE_MUTE = 'mute'


class App(Tk):
    colors = {
        'bg': '#333333',
        'active': '#bfd426',
        'active2': '#4cd426',
        'inactive': '#6b6b6b',
        'passive': '#26d4c0'
    }

    knobs = [
        [
            [
                ['steps', '',          'a', ],
                ['pulses', 'rotate',   's', ],
                ['cycles', '',         'd', ],
                ['division', '',       'f', ],
                ['velocity', '',       'g', ],
                ['sustain', '',        'h', ],
            ],
            [
                ['repeats', 'offset',  'z', ],
                ['time', 'pace',       'x', ],
                ['voicing', 'style',   'c', ],
                ['melody', 'phrase',   'v', ],
                ['accent', 'curve',    'b', ],
                ['timing', 'delay',    'n', ],

            ]
        ],
        [
            [
                ['pitch', 'harmony',   'j', ],
                ['length', 'quantize', 'k', ],
                ['tempo', '',          'l', ],
            ],
            [
                ['scale', 'root',      'm', ],
                ['midi ch', '',        ',', ],
                ['random', 'rate',     '.', ],
            ]
        ]
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

        self.old_mode = None
        self.mode = MODE_PATTERNS
        self.control = False
        self.pattern = None
        self.bank = 0
        self.active_patterns = {i: {} for i in range(16)}  # 16 banks

        self.rows = 2
        self.cols = 8
        self.w_buttons = [[], []]

        self.torso = torso_sequencer.TorsoSequencer(
            midiout=midiout,
            lookahead=0.02,
            bpm=60,
        )

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
        # self.torso.start()

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

        for b, bank in enumerate(self.knobs):
            for r, row in enumerate(bank):
                for c, col in enumerate(row):
                    f = Frame(frames[b], bg=self.colors['bg'])
                    f.grid(row=r, column=c)
                    d = Dial(
                        parent=f,
                        command=lambda degrees, rowx=r, colx=c, bankx=b: self.dial_callback(rowx, colx, bankx, degrees),
                        zeroAxis='y',
                        fill='#aaaaaa',
                        press_command=self.dial_press,
                        release_command=self.dial_release,
                        label=col[2],
                        bg=self.colors['bg'],
                    )
                    d.pack(side=TOP, fill=BOTH)
                    lb = Label(f, text=col[0], bg=self.colors['bg'])
                    lb.pack(side=TOP, fill=BOTH)
                    lb = Label(f, text=col[1], bg=self.colors['bg'])
                    lb.pack(side=TOP, fill=BOTH)

                    self.bind(
                        f'<KeyPress-{col[2]}>',
                        d.mid_press_cb,
                    )

                    self.bind(
                        f'<KeyRelease-{col[2]}>',
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

    def dial_press(self, *args, **kwargs):
        pass

    def dial_release(self, *args, **kwargs):
        pass

    def dial_callback(self, row, col, bank, degrees):
        print("dial", row, col, bank, degrees)

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
        else:
            print(f"unknown mode {self.mode}")

        self.update(); self.update_idletasks()

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
