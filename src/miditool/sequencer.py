#!/usr/bin/env python

from collections import deque
import logging
import threading
import time
import rtmidi

from heapq import heappush, heappop

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROL_CHANGE
from rtmidi.midiutil import open_midiport, list_output_ports



# from scales import scales
from . import instruments

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
        return "@%.3f %r" % (self.tick, self.message)

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


class Sequencer(threading.Thread):
    def __init__(self, midiout, queue=None, bpm=120.0, ppqn=480):
        super().__init__()
        self.midiout = midiout

        # inter-thread communication
        self.queue = queue
        if queue is None:
            self.queue = deque()

        self._stopped = threading.Event()
        self._finished = threading.Event()

        # Counts elapsed ticks when sequence is running
        self._tickcnt = None
        # Max number of input queue events to get in one loop
        self._batchsize = 100

        # run-time options
        self.ppqn = ppqn
        self.bpm = bpm

    @property
    def bpm(self):
        """Return current beats-per-minute value."""
        return self._bpm

    @bpm.setter
    def bpm(self, value):
        self._bpm = value
        self._tick = 60. / value / self.ppqn

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def add(self, event, tick=None, delta=0):
        """Enqueue event for sending to MIDI output."""
        if tick is None:
            tick = self._tickcnt or 0

        if not isinstance(event, MidiEvent):
            event = MidiEvent(tick, event)

        if not event.tick:
            event.tick = tick

        event.tick += delta
        self.queue.append(event)

    def get_event(self):
        """Poll the input queue for events without blocking.
        Could be overwritten, e.g. if you passed in your own queue instance
        with a different API.
        """
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    def handle_event(self, event):
        """Handle the event by sending it to MIDI out.
        Could be overwritten, e.g. to handle meta events, like time signature
        and tick division changes.
        """
        self.midiout.send_message(event.message)

    def run(self):
        """Start the thread's main loop.
        The thread will watch for events on the input queue and either send
        them immediately to the MIDI output or queue them for later output, if
        their timestamp has not been reached yet.
        """
        # busy loop to wait for time when next batch of events needs to
        # be written to output
        pending = []
        self._tickcnt = 0

        try:
            while not self._stopped.is_set():
                due = []
                curtime = time.time()

                # Pop events off the pending queue
                # if they are due for this tick
                while True:
                    if not pending or pending[0].tick > self._tickcnt:
                        break

                    evt = heappop(pending)
                    heappush(due, evt)

                # Pop up to self._batchsize events off the input queue
                for i in range(self._batchsize):
                    evt = self.get_event()

                    if not evt:
                        break

                    if evt.tick <= self._tickcnt:
                        heappush(due, evt)
                    else:
                        heappush(pending, evt)

                # If this batch contains any due events,
                # send them to the MIDI output.
                if due:
                    for i in range(len(due)):
                        self.handle_event(heappop(due))

                # loop speed adjustment
                elapsed = time.time() - curtime

                if elapsed < self._tick:
                    time.sleep(self._tick - elapsed)

                self._tickcnt += 1
        except KeyboardInterrupt:
            pass

        self._finished.set()


class StepSequencer(threading.Thread):
    def __init__(
        self, midiout, bpm=120.0, loop=True, ppqn=240, batchsize=100, rows=8, cols=8, pages=1,
        column_callback=None,
    ):
        super().__init__()
        self.midiout = midiout
        self.loop = loop
        self.ppqn = ppqn
        self.batchsize = batchsize
        self.rows = rows
        self.cols = cols
        self.pages = {
            p: [[None for row in range(rows)] for col in range(self.cols)] for p in range(pages)
        }
        self.column_callback = column_callback

        self.tick = None
        self.bpm = None
        self.tickcnt = 0
        self.loop_tickcnt = 0
        self.col = 0
        self.pending = []
        self.do_add = True

        self._stopped = threading.Event()
        self._finished = threading.Event()

        self.set_bpm(bpm)

    def set_bpm(self, value):
        self.bpm = value
        self.tick = 60. / value / self.ppqn

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def toggle(self, col, row, velocity=127, page=0):
        if self.pages[page][col][row] is None:
            self.pages[page][col][row] = velocity
            return True
        else:
            self.pages[page][col][row] = None
            return False

    def add(self, col, row, velocity=127, page=0):
        self.pages[page][col][row] = velocity

    def remove(self, col, row, page=0):
        self.pages[page][col][row] = None

    def handle_event(self, event):
        # print(f"fire {self.tickcnt} {event.message}")
        self.midiout.send_message(event.message)

    def get_note(self, page, row):
        these = [0, 2, 4, 5, 7, 9, 11, 12]
        return 54 + these[row]

    def fill_pending_col(self, col):
        events = []
        for p, grid in self.pages.items():
            events += [(p, i, x) for i, x in enumerate(grid[col]) if x]
        if events:
            tick = self.loop_tickcnt + col*self.ppqn
            if tick < self.tickcnt:
                tick += self.cols*self.ppqn
            tickoff = tick + self.ppqn - 1
            # print(f"fill pending {col} - {tick} - {tickoff}")
            for event in events:
                page, note, velocity = event
                note = self.get_note(page, note)
                heappush(self.pending, MidiEvent(tick, [NOTE_ON+page, note, velocity]))
                heappush(self.pending, MidiEvent(tickoff, [NOTE_OFF+page, note, 0]))

    def clock(self):
        due = []

        while True:
            if not self.pending or self.pending[0].tick > self.tickcnt:
                break

            evt = heappop(self.pending)
            heappush(due, evt)

        if due:
            for i in range(len(due)):
                self.handle_event(heappop(due))

        self.tickcnt += 1
        if self.tickcnt % self.ppqn == 0:
            self.col = (self.col + 1) % self.cols
            next_col = (self.col + 1) % self.cols

            if not self.loop and next_col == 0:
                self.do_add = False

            if self.do_add:
                self.fill_pending_col(next_col)

            if self.col == 0:
                return True

            if self.column_callback:
                self.column_callback(self.col)

        return False

    def run(self):
        self.fill_pending_col(0)
        self.fill_pending_col(1)

        self.do_add = True

        start = time.time()

        try:
            while not self._stopped.is_set():
                self.loop_tickcnt = self.tickcnt
                while not self._stopped.is_set():
                    do_break = self.clock()

                    left = max(start + self.tick*self.tickcnt - time.time(), 0)
                    time.sleep(left)
                    if do_break:
                        break

                if not self.loop:
                    if not self.pending:
                        break

        except KeyboardInterrupt:
            pass

        self._finished.set()


class LaunchpadStepSequencerMode:
    def __init__(self, sequencer):
        self.mlp = None
        self.seq = sequencer
        self.page = 0

    def start(self, mlp):
        self.mlp = mlp
        self.mlp.send_cc2(self.page, 3)

    def callback(self, msg, data):
        midi_msg, offset = msg
        message = self.mlp.callback_decoder(midi_msg, data)

        if message[0] in ['NoteOn']:
            x, y = message[1:3]
            added = self.seq.toggle(x, y, velocity=127, page=self.page)

            if added:
                self.mlp.send_note_on(x, y, 51)
            else:
                self.mlp.send_note_off(x, y, 51)

        elif message[0] in ['NoteOff']:
            pass
        elif message[0] in ['CC']:
            print(message)
        elif message[0] in ['CC2'] and message[2] == 127:
            self.page = message[1]
            self.mlp.clear()
            self.mlp.send_cc2(self.page, 3)
            this = self.seq.pages[self.page]
            print(this)
            for c, col in enumerate(this):
                print(c, col)
                for r, row in enumerate(col):
                    if row:
                        self.mlp.send_note_on(c, r, 51)
        else:
            print("???", message)


class LaunchpadStepSequencer:
    def __init__(self, out_rule=None):
        if out_rule:
            midiout = rtmidi.MidiOut()
            label, index = out_rule
            matches = [x for x in enumerate(midiout.get_ports()) if label in x[1]]
            device = matches[index]
            self.midi_out = midiout.open_port(device[0], name=device[1])
        else:
            self.midi_out, port = open_midiport(
                None,
                "LaunchpadSequencer",
                use_virtual=True
            )
            time.sleep(1)

        self.seq = StepSequencer(
            self.midi_out, bpm=200, loop=True, cols=16, pages=16,
            column_callback=self.set_column
        )

        self.lp = instruments.MultiLaunchpad(
            number=2,
            modes=[
                LaunchpadStepSequencerMode(sequencer=self.seq)
            ]
        )

        self.seq.run()
        self.seq.join()

    def set_column(self, column):
        old = (column - 1) % 16
        self.lp.send_cc(old, 0)
        self.lp.send_cc(column, 55)


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