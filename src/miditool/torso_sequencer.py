import math
import logging
import threading
import time

from heapq import heappush, heappop

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROL_CHANGE


from . import instruments
from .sequencer import MidiEvent

log = logging.getLogger(__name__)


class TorsoTrack:
    accent_curves = [
        [x/100. for x in [70, 20, 70, 20, 80, 90, 20, 60, 20, 60, 20, 60, 20, 90, 80, 20, 70]],
    ]

    def __init__(
        self, channel=0, notes=None, steps=16, pulses=1, pitch=0, rotate=0, manual_steps=None,
        accent=0, accent_curve=0, sustain=0.5, division=0, velocity=64, timing=0, swing=0, repeats=0,
        offset=0, time=0, bpm=200,
    ):
        self.channel = channel
        self.notes = notes or []
        self.manual_steps = manual_steps or []
        self.pitch = pitch
        self.rotate = rotate
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

        # require re-sequencing:
        self.steps = steps
        self.pulses = pulses

        self.sequence = []

        # some internal params
        self._sequence_start = None
        self._bpm = None
        self._beat = None

    def set_bpm(self, value):
        self._bpm = value
        self._beat = 60. / value

    def generate(self):
        interval = self.steps / self.pulses

        self.sequence = [None]*self.steps

        for i in range(self.pulses):
            spot = int(i*interval)
            note = self.notes[spot % len(self.notes)]
            self.sequence[spot] = note

    def fill_lookahead(self, start, end):
        # print(start, end, (start - self._sequence_start)/self._beat, (end - self._sequence_start)/self._beat)
        first_step = math.ceil((start - self._sequence_start)/self._beat)
        last_step = math.floor((end - self._sequence_start)/self._beat)

        if last_step < first_step:
            return []

        events = []
        for step in range(first_step, last_step+1):
            note = self.sequence[step % self.steps]
            if not note:
                continue

            events.extend([
                MidiEvent(
                    (step + self.offset)*self._beat,
                    (NOTE_ON+self.channel, note, self.velocity)
                ),
                MidiEvent(
                    (step + self.offset+self.sustain)*self._beat,
                    (NOTE_OFF+self.channel, note, 0)
                ),
            ])

        return events


class TorsoSequencer(threading.Thread):
    def __init__(self, midiout, interval=0.002, lookahead=.02, bpm=200):
        super().__init__()
        self.midiout = midiout
        self.interval = interval
        self.lookahead = lookahead
        self.start_time = None
        self.last_lookahead = None
        self.pending = []

        self.tracks = {}
        self.bpm = bpm

        self._stopped = threading.Event()
        self._finished = threading.Event()

    def set_bpm(self, value):
        for t in self.tracks.values():
            t.set_bpm(value)

        self.bpm = value

    def add_track(self, track_name, track):
        self.tracks[track_name] = track
        track.set_bpm(self.bpm)
        track.generate()

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def fill_lookahead(self):
        next_lookahead = self.last_lookahead + self.lookahead
        for v in self.tracks.values():
            new = v.fill_lookahead(self.last_lookahead, next_lookahead)
            if new:
                for n in new:
                    heappush(self.pending, n)

        self.last_lookahead = next_lookahead

    def run(self):
        steps = 0
        try:
            self.start_time = time.time()
            self.last_lookahead = self.start_time
            for t in self.tracks.values():
                t._sequence_start = self.start_time

            self.fill_lookahead()
            self.fill_lookahead()
            # return

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
                    continue

                steps += 1
                left = (self.interval*steps) - (time.time() - self.start_time)
                if left <= 0:
                    print(f"overflow time {left}")
                else:
                    time.sleep(left)

        except KeyboardInterrupt:
            pass

        self._finished.set()

