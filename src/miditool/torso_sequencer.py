import logging
import threading
import time
import rtmidi

from heapq import heappush, heappop

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROL_CHANGE
from rtmidi.midiutil import open_midiport, list_output_ports



from . import instruments
from .sequencer import MidiEvent

log = logging.getLogger(__name__)


class TorsoTrack:
    def __init__(
        self, channel=None, notes=None, steps=16, pulses=1, pitch=0, rotate=0, manual_steps=None,
        accent=0, accent_curve=0, sustain=0, division=0, velocity=127, timing=0, swing=0, repeats=0,
        offset=0, time=0,
    ):
        self.channel = channel
        self.notes = notes or []
        self.steps = steps
        self.pulses = pulses
        self.pitch = pitch
        self.rotate = rotate
        self.manual_steps = manual_steps or []
        self.division = division  # ??
        self.accent = accent
        self.accent_curve = accent_curve
        self.sustain = sustain
        self.velocity = velocity
        self.timing = timing
        self.swing = swing
        self.repeats = repeats
        self.offset = offset
        self.time = time


class TorsoSequencer(threading.Thread):
    def __init__(self, midiout, interval=0.002, lookahead=0.5):
        super().__init__()
        self.midiout = midiout
        self.interval = interval
        self.lookahead = lookahead
        self.start_time = None
        self.next_lookahead = None

        self.tracks = {}

        self._stopped = threading.Event()
        self._finished = threading.Event()

    def add_track(self, track_name, track):
        self.tracks[track_name] = track

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def fill_lookahead(self, t):
        last = self.next_lookahead
        self.next_lookahead = t + self.lookahead*0.5
        print('look', t, self.next_lookahead-last, int(1e6*((self.next_lookahead-last) - self.lookahead)))
        self.midiout.send_message([NOTE_ON, 65, 127])
        # self.midiout.send_message([NOTE_OFF, 64, 127])

    def run(self):
        steps = 0
        try:
            self.start_time = time.time()
            self.next_lookahead = self.start_time
            while not self._stopped.is_set():
                t1 = time.time()
                if t1 >= self.next_lookahead:
                    self.fill_lookahead(t1)
                steps += 1
                left = (self.interval*steps) - (time.time() - self.start_time)
                if left <= 0:
                    print(f"overflow time {left}")
                else:
                    time.sleep(left)

        except KeyboardInterrupt:
            pass

        self._finished.set()

