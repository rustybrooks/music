import logging
import threading
import time

from heapq import heappush, heappop

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROL_CHANGE


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

    def get_bpm(self):
        pass

    def generate(self):
        pass

    def fill_lookahead(self, start, end):
        pass


class TorsoSequencer(threading.Thread):
    def __init__(self, midiout, interval=0.002, lookahead=1):
        super().__init__()
        self.midiout = midiout
        self.interval = interval
        self.lookahead = lookahead
        self.start_time = None
        self.next_lookahead = None
        self.last_lookahead = None
        self.pending = []

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

    def fill_lookahead(self):
        next_lookahead = self.last_lookahead + self.lookahead
        print(time.time(), self.last_lookahead, next_lookahead)
        for v in self.tracks.values():
            new = v.fill_lookahead(self.last_lookahead, self.next_lookahead)
            if new:
                for n in new:
                    heappush(self.pending, n)

        self.last_lookahead = next_lookahead

    def run(self):
        steps = 0
        try:
            self.start_time = time.time()
            self.last_lookahead = self.start_time
            self.fill_lookahead()
            self.fill_lookahead()
            print("...", time.time(), self.last_lookahead, self.next_lookahead)

            while not self._stopped.is_set():
                t1 = time.time()

                due = []
                while True:
                    if not self.pending or self.pending[0].tick > t1:
                        break
                    evt = heappop(self.pending)
                    heappush(due, evt)

                if due:
                    for i in range(len(due)):
                        self.midiout.send_message(heappop(due).message)

                if t1 >= self.last_lookahead:
                    self.fill_lookahead()
                    return

                steps += 1
                left = (self.interval*steps) - (time.time() - self.start_time)
                if left <= 0:
                    print(f"overflow time {left}")
                else:
                    time.sleep(left)

        except KeyboardInterrupt:
            pass

        self._finished.set()

