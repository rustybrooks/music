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
                ['play',     'stop',   '9'],
                [None,       None,     '0'],
                ['clear',    'copy',   '-'],
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

        self.pressed = []

        self.torso = torso_sequencer.TorsoSequencer(
            midiout=midiout,
            lookahead=0.02,
            bpm=60,
        )
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
                        command=lambda degrees, row=r, col=c: self.dial_callback(row, col, b, degrees),
                        press_command=self.dial_press,
                        release_command=self.dial_release,
                    )
                    d.pack(side=TOP, fill=BOTH)
                    lb = Label(f, text=col[0])
                    lb.pack(side=TOP, fill=BOTH)
                    lb = Label(f, text=col[1])
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
                    f = Frame(frames[b+2])
                    f.grid(row=r, column=c)
                    bt = Button(f, height=3, width=4)

                    self.bind(
                        f'<KeyPress-{col[2]}>',
                        lambda *args, row=r, col=c, **kwargs: self.button_press(row, col, b, *args, **kwargs)
                    )

                    self.bind(
                        f'<KeyRelease-{col[2]}>',
                        lambda *args, row=r, col=c, **kwargs: self.button_release(row, col, b, *args, **kwargs)
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

    def button_press(self, row, col, bank, *args, **kwargs):
        print('press', row, col, bank, *args, **kwargs)

    def button_release(self, row, col, bank, *args, **kwargs):
        print('press', row, col, bank, *args, **kwargs)

    def press(self, button, callback=None, illumuinate=None):
        self.pressed.append(button)

    def unpress(self, button, callback=None, deluminate=None):
        i = self.pressed.index(button)
        if i > -1:
            self.pressed.pop(i)

    def play_pause(self):
        self.torso.play_pause()


if __name__ == '__main__':
    app = App()
    app.mainloop()
    app.torso.join()
    app.midiout.close_port()
