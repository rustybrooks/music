import copy
import math
import logging
import threading
import time
import random

from heapq import heappush, heappop

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF


from .notes import note_to_number, number_to_note
from .scales import get_scale_numbers
from .sequencer import MidiEvent

log = logging.getLogger(__name__)

MAX_PULSE = 16


class TrackSlice:
    def __init__(
        self, steps=16, pulses=1, notes=None, rotate=0, manual_steps=None,
    ):
        self.notes = [note_to_number(x) for x in notes or []]
        self.rotate = rotate

        self.__manual_steps = manual_steps or []
        self.__manual_steps += [0]*(MAX_PULSE - len(self.__manual_steps))
        self.__pulses = pulses
        self.__steps = steps

        self.sequence = []

        self.generate()

    @property
    def steps(self):
        return self.__steps

    @steps.setter
    def steps(self, value):
        self.__steps = value
        self.generate()

    @property
    def pulses(self):
        return self.__pulses

    @pulses.setter
    def pulses(self, value):
        self.__pulses = value
        self.generate()

    @property
    def manual_steps(self):
        return self.__manual_steps

    @manual_steps.setter
    def manual_steps(self, value):
        self.__manual_steps = value
        self.generate()

    def generate(self):
        pulses = min(self.pulses, self.steps)
        interval = self.steps / pulses
        sequence = [0]*self.steps
        print(f"[self.track_name] pulses={pulses} interval={interval} steps={self.steps} sequence={sequence}")

        for i in range(pulses):
            sequence[round(i*interval)] = 1

        for i, v in enumerate(self.manual_steps):
            if v < 0:
                sequence[i] = 0
            elif v > 0:
                sequence[i] = v

        self.sequence = sequence


class TorsoTrack:
    divisions = [
        1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64,
    ]

    accent_curves = [
        [ 70,  20,  70,  20,  80,  90,  20,  60,  20,  60,  20,  60,  20,  90,  80,  20],
        [ 30,  20,  90,  30,  25,  20,  40,  50,  40,  70,  40,  30,  35,  60,  40,  25],
        [ 30,  40,  60,  30,  40,  40, 100,  35,  30,  35,  60,  40,  70,  40, 100,  20],
        [ 25,  60,  30,  35,  80,  25,  30,  60,  25,  35,  45,  80,  35,  45,  80,  35],
        [ 90,  25,  40,  65,  90,  25,  40,  65,  90,  25,  40,  65,  90,  25,  40,  65],
        [ 85,  15,  25,  55,  50,  15,  25,  85,  50,  10,  40,  50,  45,  10,  45,  55],
        [100,  15,  20,  25,  35,  45, 100,  15, 100,  15,  35,  15,  60,  15,  25,  35],
        [ 70,  20,  20,  70,  20,  70,  20,  70,  70,  20,  70,  70,  20,  70,  20,  20],
        [  5,  12,  24,  36,  50,  62,  74,  86, 100,  12,  24,  36,  50,  62,  74,  86],
        [100,  86,  74,  62,  50,  36,  24,  12, 100,  86,  74,  62,  50,  36,  24,  12],
        [  0,  25,  50,  75,  100, 75,  50,  25,   0,  25,  50,  75, 100,  75,  50,  25],
        [100,  75,  50,  25,    0, 25,  50,  75, 100,  75,  50,  25,   0,  25,  50,  75],
    ]
    accent_curves = [[128*x/100. for x in c] for c in accent_curves]
    scales = [
        'chromatic', 'major', 'harmonic_minor', 'melodic_minor', 'hex', 'aug', 'pentatonic_minor'
    ]
    styles = ['chord', 'updward', 'downward', 'converge', 'diverge', 'random']

    phrases = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 0, 0],
        [0, 1, 3, 2, 5, 4, 6, 5, 7, 6, 8, 7, 9],
        [0, 1, 5, 6, 2, 7, 8, 4, 3, 1, 0, 1, 2, 3],
    ]

    def __init__(
        self, channel=0,
        slices=None,
        pitch=0,  # pitch shift to apply to all notes, integer (FIXME add intelligent shifting?)
        harmony=0,  # transpose notes defined in pitch up one at a time?
        accent=.5,  # 0-1 the percent of accent curve to apply
        accent_curve=0,  # select from predefined accent curves (FIXME make some)
        sustain=0.15,  # Note length, in increments of step, i.e. 0.5 = half step
        division=4,  # how many pieces to divide a beat into
        velocity=64,  # base velocity - accent gets added to this
        timing=0.5,  # swing timing, 0.5=even, less means every other beat is early, more means late
        delay=0,  # delay pattern in relation to other patterns, +ve means later, in units of beat
        repeats=0,  # number of repeats to add, integer, will be is divisions of self.time
        repeat_offset=0,  # this delays the repeats, in units of 1 beat
        repeat_time=1,  # this is the same as divsion, but for repeats, minimum is 1
        repeat_pace=None,  # supposed to accelerate or decelerate repeats - not implemented
        voicing=0,  # adds notes an octave above
        style=0,  # integer, picks
        melody=0,  # "depth" LFO for phrase (speed?)
        phrase=0,  # integer, picks phrase from a list
        scale=0,  # integer, picks scale from a list for phrase to operate on (default = chromatic)
        root=0,
        random=None,
        random_rate=None,
        muted=False,
        **kwargs,  # to absorb anything else added to the track files
    ):
        self.__slice_index = 0
        self.__slice_step = 0
        self.__bpm = None
        self.__scale = None
        self.__scale_type = None
        self.__root = root

        self.muted = muted
        self.track_name = None

        self.slices = slices or [TrackSlice()]

        self.channel = channel

        self.pitch = pitch
        self.division = division  # ??
        self.accent = accent
        self.sustain = sustain
        self.velocity = velocity
        self.timing = timing
        self.delay = delay
        self.repeats = repeats
        self.repeat_offset = repeat_offset
        self.repeat_time = repeat_time
        self.repeat_pace = repeat_pace
        self.melody = melody
        self.harmony = harmony
        self.voicing = voicing
        self.scale = scale
        self.root = root

        self.phrase = None
        self.accent_curve = None
        self.style = None

        self.accent_curve = self.accent_curves[accent_curve]
        self.style = self.styles[style]
        self.phrase = self.phrases[phrase]

        self.randoms = {}

        # some internal params
        self._sequence_start = None
        self._beat = None
        self._step = 1

    def add_slice(self, slice):
        self.slices.append(slice)
        if self.slice is None:
            self.slice = 0

    @property
    def scale(self):
        return self.__scale

    @scale.setter
    def scale(self, value):
        if value in self.scales:
            value = self.scales.index(value)
        self.__scale = get_scale_numbers(self.__root, scale_type=self.scales[value], octaves=10)
        self.__scale_type = self.scales[value]

    @property
    def root(self):
        return self.__scale

    @root.setter
    def root(self, value):
        self.__scale = get_scale_numbers(self.__root, scale_type=self.__scale_type, octaves=10)

    @property
    def slice(self):
        return self.slices[self.__slice_index]

    @slice.setter
    def slice(self, value):
        self.__slice_index = value
        self.voicing = self.__voicing  # to trigger a recalc of voicing

    @property
    def notes(self):
        return self.slice.notes

    @notes.setter
    def notes(self, value):
        self.slice.notes = value

    @property
    def steps(self):
        return self.slice.steps

    @steps.setter
    def steps(self, value):
        self.slice.steps = value

    @property
    def pulses(self):
        return self.slice.pulses

    @pulses.setter
    def pulses(self, value):
        self.slice.pulses = value

    @property
    def manual_steps(self):
        return self.slice.manual_steps

    @manual_steps.setter
    def manual_steps(self, value):
        self.slice.manual_steps = value

    @property
    def rotate(self):
        return self.slice.rotate

    @rotate.setter
    def rotate(self, value):
        self.slice.rotate = value

    @property
    def bpm(self):
        return self.__bpm

    @bpm.setter
    def bpm(self, value):
        self.__bpm = value
        self._beat = 60. / (value)

    @property
    def sequence(self):
        return self.slice.sequence

    @property
    def voicing(self):
        return self.__voicing

    @voicing.setter
    def voicing(self, value):
        self.__voicing = value
        # print(f"slice notes {self.slice.notes}")
        self.__voiced_notes = sorted(copy.deepcopy(self.slice.notes))
        ln = len(self.slice.notes)
        for v in range(value):
            n = self.slice.notes[v % ln]
            self.__voiced_notes.append(n + 12*(1+v//ln))

        # print(f"[{self.track_name}] voicing settr, value={value} notes={self.slice.notes} voiced notes={self.__voiced_notes}")

    @property
    def voiced_notes(self):
        return self.__voiced_notes

    def update_random(self, parameter, strength):
        if parameter not in self.randoms:
            self.randoms[parameter] = [0] * MAX_PULSE

        for i in range(MAX_PULSE):
            self.randoms[parameter][i] += random.randrange(-strength, strength)

    def add_note_quantized(self, note, offset):
        # quantize note first
        qnote = self.quantize(note)
        notei = self.scale.index(qnote)
        snote = self.scale[int(round(notei+offset))]
        # print(f"note={note} quant={qnote} {number_to_note(qnote) }-- offset={offset} ({int(round(notei+offset))}), notei={notei}, scalenote={snote} {number_to_note(snote)}")
        return snote

    def quantize(self, note):
        overi = next(i for i, n in enumerate(self.scale) if n > note)
        underi = overi-1
        # print(self.scale)
        # print(f"note={note} overi={overi} overi-s={self.scale[overi]} underi-s={self.scale[underi]}")

        if (note - self.scale[underi]) < (self.scale[overi] - note):
            val = self.scale[underi]
        else:
            val = self.scale[overi]

        return val

    def style_notes(self, index):
        return [self.voiced_notes[index % len(self.voiced_notes)]]

    def fill_lookahead(self, start, end):
        # not sure it's right to add delay in here...  if we only hve +ve delay we def don't
        # need to
        first_step = math.ceil(self.division*(start - self._sequence_start + self.delay*self._beat)/self._beat)
        last_step = math.floor(self.division*(end - self._sequence_start + self.delay*self._beat)/self._beat)

        if last_step < first_step:
            return []

        events = []
        for step in range(first_step, last_step+1):
            if step - self.__slice_step >= self.slice.steps:
                self.slice = (self.__slice_index+1) % len(self.slices)
                self.__slice_step = step

            if not self.slice.sequence[(step-self.slice.rotate) % self.slice.steps]:
                continue

            melody_offset = self.phrase[(step - self.slice.rotate) % len(self.phrase)]*self.melody
            accent = self.accent_curve[(step-self.slice.rotate) % len(self.accent_curve)]*self.accent
            velocity = min(int(self.velocity + accent), 127)
            swing = 0 if step % 2 == 0 else (self.timing-0.5)

            for r in range(0, self.repeats+1):
                notes = self.style_notes(r)
                for note in notes:
                    note = self.add_note_quantized(note, melody_offset)
                    events.extend([
                        MidiEvent(
                            (step + swing + self.delay + self.repeat_offset + (r/self.repeat_time))*self._beat/self.division,
                            (NOTE_ON+self.channel, note+self.pitch, velocity)
                        ),
                        MidiEvent(
                            (step + self.sustain + self.delay + self.repeat_offset + r/self.repeat_time)*self._beat/self.division,
                            (NOTE_OFF+self.channel, note+self.pitch, 0)
                        ),
                    ])

        return events


class TorsoSequencer(threading.Thread):
    def __init__(self, midiout, interval=0.003, lookahead=.01, bpm=200):
        super().__init__()
        self.midiout = midiout
        self.interval = interval
        self.lookahead = lookahead
        self._start_time = None
        self._last_lookahead = None
        self.pending = []

        self.tracks = {}
        self.bpm = bpm

        self._stopped = threading.Event()
        self._finished = threading.Event()
        self._paused = threading.Event()

    def set_bpm(self, value):
        for t in self.tracks.values():
            t.set_bpm(value)

        self.bpm = value

    def add_track(self, track_name, track):
        self.tracks[track_name] = track
        track.bpm = self.bpm
        track.track_name = track_name

    def get_track(self, track_name, create=True):
        if track_name not in self.tracks and create:
            self.add_track(track_name, TorsoTrack())

        return self.tracks.get(track_name)

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def play_pause(self):
        if self._paused.is_set():
            self._paused.clear()
        else:
            self._paused.set()

    def pause(self):
        self._paused.set()

    def fill_lookahead(self):
        next_lookahead = self._last_lookahead + self.lookahead
        for v in self.tracks.values():
            if v.muted:
                continue

            new = v.fill_lookahead(self._last_lookahead, next_lookahead)
            if new:
                for n in new:
                    heappush(self.pending, n)

        self._last_lookahead = next_lookahead

    def reset(self):
        self._step = 0
        self.pending = []
        self._start_time = time.time()
        self._last_lookahead = self._start_time
        for t in self.tracks.values():
            t._sequence_start = self._start_time

        self.fill_lookahead()
        self.fill_lookahead()

    def run(self):
        try:
            self.reset()

            while not self._stopped.is_set():
                reset = False
                while self._paused.is_set():
                    time.sleep(.2)
                    reset = True
                else:
                    if reset:
                        self.reset()

                t1 = time.time()
                t1o = t1 - self._start_time
                due = []
                while True:
                    if not self.pending or self.pending[0].tick > t1o:
                        break
                    evt = heappop(self.pending)
                    heappush(due, evt)

                if due:
                    for i in range(len(due)):
                        m = heappop(due)
                        self.midiout.send_message(m.message)

                if t1 >= self._last_lookahead:
                    self.fill_lookahead()
                    continue

                self._step += 1
                left = (self.interval*self._step) - (time.time() - self._start_time)
                if left <= 0:
                    print(f"overflow time {1000*left:.2f}ms")
                else:
                    time.sleep(left)

        except KeyboardInterrupt:
            pass

        self._finished.set()

