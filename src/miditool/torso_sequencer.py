import math
import logging
import threading
import time
import random

from heapq import heappush, heappop

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF


from .notes import note_to_number
from .scales import get_scale_numbers
from .sequencer import MidiEvent

log = logging.getLogger(__name__)

MAX_PULSE = 16


class TorsoTrack:
    accent_curves = [
        [128*x/100. for x in [70, 20, 70, 20, 80, 90, 20, 60, 20, 60, 20, 60, 20, 90, 80, 20, 70]],
    ]
    scales = [
        'chromatic', 'major', 'harmonic_minor', 'melodic_minor', 'hex', 'aug', 'pentatonic_minor'
    ]
    styles = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        [0, 2, 1, 3, 2, 4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9, 8],
    ]

    phrases = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    ]

    def __init__(
        self, channel=0, steps=16,
        pulses=1,  # number of euclidean pulses to apply, 1 to steps
        pitch=0,  # pitch shift to apply to all notes, integer (FIXME add intelligent shifting?)
        harmony=0,  # transpose notes defined in pitch up one at a time?
        notes=None,  # List of notes to play
        rotate=0,  # number of steps to rotate sequence
        manual_steps=None,  # list of manual locations to apply hits, -1=remove, 0=nothing, 1=add
        accent=.5,  # 0-1 the percent of accent curve to apply
        accent_curve=0,  # select from predefined accent curves (FIXME make some)
        sustain=0.15,  # Note length, in increments of step, i.e. 0.5 = half step
        division=1,  # how many pieces to divide a beat into
        velocity=64,  # base velocity - accent gets added to this
        timing=0.5,  # swing timing, 0.5=even, less means every other beat is early, more means late
        delay=0,  # delay pattern in relation to other patterns, +ve means later, in units of beat
        repeats=0,  # number of repeats to add, integer, will be is divisions of self.time
        repeat_offset=0,  # this delays the repeats, in units of 1 beat
        repeat_time=2,  # this is the same as divion, but for repeats, minimum is 2
        pace=None,  # supposed to accelerate or decelerate repeats - not implemented
        voicing=0,  # adds notes an octave above, 1 means just first note
        style=0,  # integer, picks
        melody=0,  # "depth" LFO for phrase (speed?)
        phrase=0,  # integer, picks phrase from a list
        scale=0,  # integer, picks scale from a list for phrase to operate on (default = chromatic)
        root=0,
        random=None,
        random_rate=None,
    ):
        self.channel = channel
        self.notes = [note_to_number(x) for x in notes] or []
        self.manual_steps = manual_steps or []
        self.pitch = pitch
        self.rotate = rotate
        self.division = division  # ??
        self.accent = accent
        self.sustain = sustain
        self.velocity = velocity
        self.timing = timing
        self.delay = delay
        self.repeats = repeats
        self.repeat_offset = repeat_offset
        self.repeat_time = repeat_time
        self.pace = pace
        self.voicing = voicing
        self.melody = melody

        self.phrase = None
        self.accent_curve = None
        self.style = None
        self.scale = None

        self.set_accent_curve(accent_curve)
        self.set_style(style)
        self.set_scale(scale, root=root)
        self.set_phrase(phrase)

        # require re-sequencing:
        self.steps = steps
        self.pulses = pulses

        self.sequence = []
        self.randoms = {}

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

    def set_style(self, value):
        self.style = self.styles[value]

    def set_scale(self, value, root):
        self.scale = get_scale_numbers(root-root, scale_type=self.scales[value])

    def set_phrase(self, value):
        self.phrase = self.phrases[value]

    def update_random(self, parameter, strength):
        if parameter not in self.randoms:
            self.randoms[parameter] = [0] * MAX_PULSE

        for i in range(MAX_PULSE):
            self.randoms[parameter][i] += random.randrange(-strength, strength)

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

        self.sequence = sequence

        # lnotes = len(self.notes)
        # self.sequence = [self.notes[i % lnotes] if v else None for i, v in enumerate(sequence)]

    def quantize(self, note):
        root = self.scale[0]
        while root > note:
            root -= 12

        while root+12 < note:
            root += 12

        diff = root - self.scale[0]
        scale = [x+diff for x in self.scale]
        overi = next(i for i, n in enumerate(scale) if n > note)
        if overi is None:
            overi = len(scale)
            scale.append(scale[0]+12)

        underi = overi-1

        if (note - scale[underi]) < (scale[overi] - note):
            return scale[underi]
        else:
            return scale[overi]

    def fill_lookahead(self, start, end):
        # not sure it's right to add delay in here...  if we only hve +ve delay we def don't
        # need to
        first_step = math.ceil(self.division*(start - self._sequence_start + self.delay*self._beat)/self._beat)
        last_step = math.floor(self.division*(end - self._sequence_start + self.delay*self._beat)/self._beat)

        if last_step < first_step:
            return []

        events = []
        lnotes = len(self.notes)
        for step in range(first_step, last_step+1):
            if not self.sequence[(step+self.rotate) % self.steps]:
                continue

            note = self.notes[0]
            melody_offset = None
            if self.melody > 0:
                melody_offset = note + self.phrase[step]*self.melody
                note = self.quantize(note + melody_offset)

            # do we want to step through accent curve, or apply it directly to sequence including
            # off notes?
            accent = (self.accent_curve[(step+self.rotate) % len(self.accent_curve)])*self.accent
            velocity = min(int(self.velocity + accent), 127)
            swing = 0 if step % 2 == 0 else (self.timing-0.5)
            vleft = (self.voicing+1+self.repeats) % (self.repeats+1)
            vmax = (vleft >= 0) + (self.voicing+1+self.repeats)//(self.repeats+1)
            for voicing in range(0, vmax):
                events.extend([
                    MidiEvent(
                        (step + swing + self.delay)*self._beat/self.division,
                        (NOTE_ON+self.channel, note+self.pitch+voicing*12, velocity)
                    ),
                    MidiEvent(
                        (step + self.sustain + self.delay)*self._beat/self.division,
                        (NOTE_OFF+self.channel, note+self.pitch+voicing*12, 0)
                    ),
                ])

            for r in range(1, self.repeats+1):
                note = self.notes[self.style[r % len(self.sequence)] % lnotes]
                if melody_offset:
                    note = self.quantize(melody_offset)

                vmax = (vleft >= r) + (self.voicing+1+self.repeats)//(self.repeats+1)

                print("repeat", r, vmax, self.voicing // (1+self.repeats))

                for voicing in range(0, vmax):
                    events.extend([
                        MidiEvent(
                            (step + swing + self.delay + self.repeat_offset + (r/self.repeat_time))*self._beat/self.division,
                            (NOTE_ON+self.channel, note+self.pitch+voicing*12, velocity)
                        ),
                        MidiEvent(
                            (step + self.sustain + self.delay + self.repeat_offset + r/self.repeat_time)*self._beat/self.division,
                            (NOTE_OFF+self.channel, note+self.pitch+voicing*12, 0)
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
                        # print(f"{t1o:.04f} - self.start_time {m}")
                        self.midiout.send_message(m.message)

                if t1 >= self.last_lookahead:
                    self.fill_lookahead()
                    continue

                steps += 1
                left = (self.interval*steps) - (time.time() - self.start_time)
                if left <= 0:
                    print(f"overflow time {1000*left:.2f}ms")
                else:
                    time.sleep(left)

        except KeyboardInterrupt:
            pass

        self._finished.set()

