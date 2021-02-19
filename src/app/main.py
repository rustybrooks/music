#!/usr/bin/env python

import os, sys
basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
sys.path.append(lp)


from tkinter import *
from app.dial import Dial

from miditool import torso_sequencer, notes
from rtmidi.midiutil import open_midiport
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF


class App(Tk):
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
                ['ctrl',     '',       '='],
            ],
            [
                ['bank',    'save',    'p'],
                ['pattern', 'select',  '['],
                ['temp',    'multi',   ']'],
                ['mute',     '',       '\\'],
            ],
        ],
    ]

    def __init__(self):
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

        self.torso = torso_sequencer.TorsoSequencer(
            midiout=midiout,
            lookahead=0.02,
            bpm=60,
        )

        tp = torso_sequencer.TorsoTrack(
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
        self.torso.add_track(track_name='piano', track=tp)

        self.torso.pause()
        self.torso.start()

        Tk.__init__(self)
        self.title("boobs")

        fl = Frame(self, border=10)
        fm = Frame(self, width=10)
        fr = Frame(self, border=10)
        fl.pack(side=LEFT, fill=X)
        fm.pack(side=LEFT, fill=NONE)
        fr.pack(side=LEFT, fill=X)

        flt = Frame(fl)
        flb = Frame(fl)
        flt.pack(side=TOP, fill=BOTH)
        flb.pack(side=TOP, fill=BOTH, pady=[50, 0])

        frt = Frame(fr)
        frb = Frame(fr)
        frt.pack(side=TOP, fill=BOTH)
        frb.pack(side=TOP, fill=BOTH, pady=[50, 0])

        frames = [flt, frt, flb, frb]

        for b, bank in enumerate(self.knobs):
            for r, row in enumerate(bank):
                for c, col in enumerate(row):
                    f = Frame(frames[b])
                    f.grid(row=r, column=c)
                    d = Dial(
                        parent=f, zeroAxis='y', fill='#aaaaaa',
                        command=lambda degrees, rowx=r, colx=c, bankx=b: self.dial_callback(rowx, colx, bankx, degrees),
                        press_command=self.dial_press,
                        release_command=self.dial_release,
                        label=col[2],
                    )
                    d.pack(side=TOP, fill=BOTH)
                    lb = Label(f, text=col[0])
                    lb.pack(side=TOP, fill=BOTH)
                    lb = Label(f, text=col[1])
                    lb.pack(side=TOP, fill=BOTH)

                    print(f'<KeyPress-{col[2]}>')
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

                    f = Frame(frames[b+2])
                    f.grid(row=r, column=c)
                    bt = Button(f, height=3, width=4, text=col[2])

                    print(f'<KeyPress-{col[2]}>')
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
                        lambda *args, row=r, col=c, **kwargs: self.button_press(row, col, b, *args, **kwargs)
                    )
                    bt.bind(
                        '<ButtonRelease>',
                        lambda *args, row=r, col=c, **kwargs: self.button_release(row, col, b, *args, **kwargs)
                    )
                    bt.pack(side=TOP, fill=X)
                    lb = Label(f, text=col[0])
                    lb.pack(side=TOP, fill=X)
                    lb = Label(f, text=col[1])
                    lb.pack(side=TOP, fill=X)

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
        cmd = self.button_command(row, col, bank, press=True)
        if cmd:
            cmd()

    def button_release(self, row, col, bank, event, *args, **kwargs):
        bkey = (row, col, bank)

        self.has_prev_key_release[bkey] = None

        if bkey not in self.button_pressed:
            return

        self.button_pressed.pop(bkey)

        print(f'release row={row} col={col} bank={bank} event={event} serial={event.serial}')
        cmd = self.button_command(row, col, bank, press=False)
        if cmd:
            cmd()

    def play_pause(self):
        print("play_pause")
        self.torso.play_pause()


if __name__ == '__main__':
    app = App()
    app.mainloop()
    app.torso.join()
    app.midiout.close_port()
