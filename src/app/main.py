#!/usr/bin/env python

import os, sys
basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
sys.path.append(lp)


from tkinter import *
from app.dial import Dial

import time
from miditool import torso_sequencer, notes
from rtmidi.midiutil import open_midiport
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from miditool.sequencer import Sequencer


knobs1 = [
    [
        ['steps', ''],
        ['pulses', 'rotate'],
        ['cycles', ''],
        ['division', ''],
        ['velocity', ''],
        ['sustain', ''],
    ],
    [
        ['repeats', 'offset'],
        ['time', 'pace'],
        ['voicing', 'style'],
        ['melody', 'phrase'],
        ['accent', 'curve'],
        ['timing', 'delay'],

    ]
]

knobs2 = [
    [
        ['pitch', 'harmony'],
        ['length', 'quantize'],
        ['tempo', ''],
    ],
    [
        ['scale', 'root'],
        ['midi ch', ''],
        ['random', 'rate'],
    ]
]

buttons1 = [
    [
        ['/1', ''],
        ['/2', ''],
        ['/4', ''],
        ['/8', ''],
        ['/16', ''],
        ['/32', ''],
        ['/64', ''],
        ['', ''],
    ],
    [
        ['', 'chrom'],
        ['', 'major', ''],
        ['/3', 'minor'],
        ['/6', 'melo'],
        ['/12', 'hex'],
        ['/24', 'aug'],
        ['/48', 'penta'],
        ['', 'user'],
    ]
]

buttons2 = [
    [
        ['play', 'stop'],
        [None, None],
        ['clear', 'copy'],
        ['ctrl', ''],
    ],
    [
        ['bank', 'save'],
        ['pattern', 'select'],
        ['temp', 'multi'],
        ['mute', ''],
    ],
]


class App(Tk):
    def __init__(self):
        midiout, port = open_midiport(
            None,
            "TORSO",
            use_virtual=True,
            client_name="TORSO"
        )

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

        for r, row in enumerate(knobs1):
            for c, col in enumerate(row):
                f = Frame(flt)
                f.grid(row=r, column=c)
                d = Dial(parent=f, command=lambda degrees, row=r, col=c: self.dial_callback(row, col, degrees))
                d.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[0])
                l.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[1])
                l.pack(side=TOP, fill=BOTH)

        for r, row in enumerate(buttons1):
            for c, col in enumerate(row):
                f = Frame(flb)
                f.grid(row=r, column=c)
                b = Button(f, height=3, width=4)
                b.pack(side=TOP, fill=X)
                l = Label(f, text=col[0])
                l.pack(side=TOP, fill=X)
                l = Label(f, text=col[1])
                l.pack(side=TOP, fill=X)

        for r, row in enumerate(knobs2):
            for c, col in enumerate(row):
                f = Frame(frt)
                f.grid(row=r, column=c)
                d = Dial(parent=f, command=lambda degrees, row=r, col=c: self.dial_callback(row, col, degrees))
                d.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[0])
                l.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[1])
                l.pack(side=TOP, fill=BOTH)

        for r, row in enumerate(buttons2):
            for c, col in enumerate(row):
                f = Frame(frb)
                f.grid(row=r, column=c)
                b = Button(f, height=3, width=4)
                b.pack(side=TOP, fill=X)
                l = Label(f, text=col[0])
                l.pack(side=TOP, fill=X)
                l = Label(f, text=col[1])
                l.pack(side=TOP, fill=X)

    def dial_callback(self, *args, **kwargs):
        print("dial", args, kwargs)


if __name__ == '__main__':
    app = App()
    app.mainloop()
    app.torso.join()
    app.midiout.close_port()
