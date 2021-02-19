#!/usr/bin/env python

import os, sys
basedir = os.path.dirname(os.path.realpath(__file__))
lp = os.path.abspath(os.path.join(basedir, '..'))
sys.path.append(lp)


from tkinter import *
from app.dial import Dial


buttons1 = [
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

buttons2 = [
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

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("boobs")

        fl = Frame(self, border=10)
        fm = Frame(self, width=10)
        fr = Frame(self, border=10)
        fl.pack(side=LEFT, fill=X)
        fm.pack(side=LEFT, fill=NONE)
        fr.pack(side=LEFT, fill=X)

        flt = Frame(fl)
        flb = Frame(fl, background='red')
        flt.pack(side=TOP, fill=BOTH)
        flb.pack(side=TOP, fill=BOTH)

        frt = Frame(fr)
        frb = Frame(fr)
        frt.pack(side=TOP, fill=BOTH)
        frb.pack(side=TOP, fill=BOTH)

        for r, row in enumerate(buttons1):
            for c, col in enumerate(row):
                f = Frame(flt)
                f.grid(row=r, column=c)
                d = Dial(parent=f)
                d.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[0])
                l.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[1])
                l.pack(side=TOP, fill=BOTH)

            for r in range(2):
                for c in range(8):
                    b = Button(flb, height=3, width=4)
                    b.grid(row=r, column=c)

        for r, row in enumerate(buttons2):
            for c, col in enumerate(row):
                f = Frame(frt)
                f.grid(row=r, column=c)
                d = Dial(f)
                d.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[0])
                l.pack(side=TOP, fill=BOTH)
                l = Label(f, text=col[1])
                l.pack(side=TOP, fill=BOTH)

            for r in range(2):
                for c in range(4):
                    b = Button(frb, height=3, width=4)
                    b.grid(row=r, column=c)



if __name__ == '__main__':
    app = App()
    app.mainloop()
