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
        [128*x/100. for x in [70, 20, 70, 20, 80, 90, 20, 60, 20, 60, 20, 60, 20, 90, 80, 20, 70]],
    ]
    divisions = [
        1, 2, 4, 8, 16, 32, 64, 0,
        0, 0, 3, 6, 12, 24, 48, 0
    ]

    def __init__(
        self, channel=0, notes=None, steps=16,
        pulses=1,  # number of euclidean pulses to apply, 1 to steps
        pitch=0,  # pitch shift to apply to all notes, integer (FIXME add intelligent shifting?)
        harmony=None,
        rotate=0,  # number of steps to rotate sequence
        manual_steps=None,  # list of manual locations to apply hits, -1=remove, 0=nothing, 1=add
        accent=.5,  # 0-1 the percent of accent curve to apply
        accent_curve=0,  # select from predefined accent curves (FIXME make some)
        sustain=0.5,  # Note length, in increments of step, i.e. 0.5 = half step
        division=1,  # how many pieces to divide a beat into
        velocity=64,  # base velocity - accent gets added to this
        timing=0.5,  # swing timing, 0.5=even, less means every other beat is early, more means late
        delay=0,
        repeats=0,
        offset=0,
        time=0,
        pace=None,
        voicing=None,
        melody=None,
        phrase=None,
        scale=None,
        root=None,
    ):
        self.channel = channel
        self.notes = notes or []
        self.manual_steps = manual_steps or []
        self.pitch = pitch
        self.rotate = rotate
        self.division = division  # ??
        self.accent = accent
        self.sustain = sustain
        self.velocity = velocity
        self.timing = timing
        self.repeats = repeats
        self.offset = offset
        self.time = time

        self.accent_curve = None
        self.set_accent_curve(accent_curve)

        # requires updating some other param

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
        # self._beat = 60. / (value*self.division)
        self._beat = 60. / (value)

    # # FIXME come back and clean up the math when I'm sure it works
    # def set_division(self, value, now=None):
    #     now = now or time.time()
    #     old_offset = now - self._sequence_start
    #     multiplier = self.division / value
    #     new_offset = old_offset * multiplier
    #     self._sequence_start = now - new_offset

    def set_accent_curve(self, value):
        self.accent_curve = self.accent_curves[value]

    def generate(self):
        interval = self.steps / self.pulses

        sequence = [0]*self.steps

        for i in range(self.pulses):
            sequence[int(i*interval)] = 1

        for i, v in enumerate(self.manual_steps):
            if v < 0:
                sequence[i] = 0
            elif v > 0:
                sequence[i] = v

        lnotes = len(self.notes)
        self.sequence = [self.notes[i % lnotes] if v else None for i, v in enumerate(sequence)]

    def fill_lookahead(self, start, end):
        first_step = math.ceil(self.division*(start - self._sequence_start)/self._beat)
        last_step = math.floor(self.division*(end - self._sequence_start)/self._beat)

        if last_step < first_step:
            return []

        events = []
        for step in range(first_step, last_step+1):
            note = self.sequence[(step+self.rotate) % self.steps]
            if not note:
                continue

            # do we want to step through accent curve, or apply it directly to sequence including
            # off notes?
            accent = (self.accent_curve[(step+self.rotate) % len(self.accent_curve)])*self.accent
            velocity = min(int(self.velocity + accent), 127)
            swing = 0 if step % 2 == 0 else (self.timing-0.5)
            events.extend([
                MidiEvent(
                    (step + self.offset + swing)*self._beat/self.division,
                    (NOTE_ON+self.channel, note+self.pitch, velocity)
                ),
                MidiEvent(
                    (step + self.offset + self.sustain)*self._beat/self.division,
                    (NOTE_OFF+self.channel, note+self.pitch, 0)
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
                t1o = t1 - self.start_time
                due = []
                while True:
                    if not self.pending or self.pending[0].tick > t1o:
                        break
                    evt = heappop(self.pending)
                    heappush(due, evt)

                if due:
                    for i in range(len(due)):
                        m = heappop(due)
                        # print(time.time() - self.start_time, m)
                        self.midiout.send_message(m.message)

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

