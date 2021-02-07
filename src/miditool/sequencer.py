#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sequencer.py
#
"""Example of using a thread to send out queued-up, timed MIDI messages."""

import logging
import threading
import time

from heapq import heappush, heappop

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from rtmidi.midiutil import open_midiport, list_output_ports

import sys

from scales import scales

log = logging.getLogger(__name__)


class MidiEvent(object):
    """Container for a MIDI message and a timing tick.
    Bascially like a two-item named tuple, but we overwrite the comparison
    operators, so that they (except when testing for equality) use only the
    timing ticks.
    """

    __slots__ = ('tick', 'message')

    def __init__(self, tick, message):
        self.tick = tick
        self.message = message

    def __repr__(self):
        return "@ %05i %r" % (self.tick, self.message)

    def __eq__(self, other):
        return self.tick == other.tick and self.message == other.message

    def __lt__(self, other):
        return self.tick < other.tick

    def __le__(self, other):
        return self.tick <= other.tick

    def __gt__(self, other):
        return self.tick > other.tick

    def __ge__(self, other):
        return self.tick >= other.tick


class StepSequencer(threading.Thread):
    def __init__(
        self, midiout, bpm=120.0, loop=True, ppqn=480, batchsize=100, rows=8, cols=8,
    ):
        super().__init__()
        self.midiout = midiout
        self.loop = loop
        self.ppqn = ppqn
        self.batchsize = batchsize
        self.rows = rows
        self.cols = cols
        self.grid = [[None for row in range(rows)] for col in range(self.cols)]

        self.tick = None
        self.bpm = None
        self.tickcnt = 0
        self.loop_tickcnt = 0
        self.col = 0

        self._stopped = threading.Event()
        self._finished = threading.Event()

        self.set_bpm(bpm)

    def set_bpm(self, value):
        self.bpm = value
        self.tick = 60. / value / self.ppqn
        print(f'tick={self.tick}')

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def add(self, col, row, velocity=127):
        self.grid[col][row] = velocity

    def get_events(self, col):
        return [x for x in self.grid[col] if x]

    def handle_event(self, event):
        # print(f"fire {self.tickcnt} {event.message}")
        self.midiout.send_message(event.message)

    def get_note(self, row):
        these = [0, 2, 4, 5, 7, 9, 11, 12]
        return 54 + these[row]

    def fill_pending_col(self, pending, col):
        events = [(i, x) for i, x in enumerate(self.grid[col]) if x]
        if events:
            tick = self.loop_tickcnt + col*self.ppqn
            if tick < self.tickcnt:
                tick += self.cols*self.ppqn
            tickoff = tick + self.ppqn - 1
            # print(f"fill pending {col} - {tick} - {tickoff}")
            for event in events:
                note = self.get_note(event[0])
                heappush(pending, MidiEvent(tick, [NOTE_ON, note, event[1]]))
                heappush(pending, MidiEvent(tickoff, [NOTE_OFF, note, 0]))

    def run(self):
        pending = []
        self.fill_pending_col(pending, 0)
        self.fill_pending_col(pending, 1)

        do_add = True

        start = time.time()

        try:
            while True:
                self.loop_tickcnt = self.tickcnt
                do_break = False

                while not self._stopped.is_set():
                    due = []

                    while True:
                        if not pending or pending[0].tick > self.tickcnt:
                            break

                        evt = heappop(pending)
                        heappush(due, evt)
                    if due:
                        for i in range(len(due)):
                            self.handle_event(heappop(due))

                    self.tickcnt += 1
                    if self.tickcnt % self.ppqn == 0:
                        self.col = (self.col + 1) % self.cols
                        next_col = (self.col + 1) % self.cols

                        if not self.loop and next_col == 0:
                            do_add = False

                        if do_add:
                            self.fill_pending_col(pending, next_col)

                        if self.col == 0:
                            do_break = True

                    left = max(start + self.tick*self.tickcnt - time.time(), 0)
                    time.sleep(left)
                    if do_break:
                        break

                if not self.loop:
                    if not pending:
                        break

        except KeyboardInterrupt:
            pass

        self._finished.set()


def _test():
    import sys

    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    try:
        midiout, port = open_midiport(
            sys.argv[1] if len(sys.argv) > 1 else None,
            "output",
            client_name="RtMidi Sequencer")
        time.sleep(1)

    except (IOError, ValueError) as exc:
        return "Could not open MIDI input: %s" % exc
    except (EOFError, KeyboardInterrupt):
        return

    seq = StepSequencer(midiout, bpm=200, ppqn=10, loop=False, cols=4)
    seq.add(0, 0)
    # seq.add(1, 1)
    seq.add(2, 2)
    seq.add(3, 2)

    try:
        seq.start()
        seq.join()
    finally:
        seq.stop()
        midiout.close_port()
        del midiout


if __name__ == '__main__':
    _test()