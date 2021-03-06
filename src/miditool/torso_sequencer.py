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
    divisions = [
        1, 2, 4, 8, 16, 32, 64,
        3, 6, 12, 24, 48,
    ]

    accent_curves = [
        [ 70,  20,  70,  20,  80,  90,  20,  60,  20,  60,  20,  60,  20,  90,  80,  20, 70 ],
        [ 30,  20,  90,  30,  25,  20,  40,  50,  40,  70,  40,  30,  35,  60,  40,  25, 30 ],
        [ 30,  40,  60,  30,  40,  40, 100,  35,  30,  35,  60,  40,  70,  40, 100,  20, 30 ],
        [ 25,  60,  30,  35,  80,  25,  30,  60,  25,  35,  45,  80,  35,  45,  80,  35, 40 ],
        [ 90,  25,  40,  65,  90,  25,  40,  65,  90,  25,  40,  65,  90,  25,  40,  65, 90 ],
        [ 85,  15,  25,  55,  50,  15,  25,  85,  50,  10,  40,  50,  45,  10,  45,  55, 80 ],
        [100,  15,  20,  25,  35,  45, 100,  15, 100,  15,  35,  15,  60,  15,  25,  35, 90 ],
        [ 70,  20,  20,  70,  20,  70,  20,  70,  70,  20,  70,  70,  20,  70,  20,  20, 70 ],
        [  5,  12,  24,  36,  50,  62,  74,  86, 100,  12,  24,  36,  50,  62,  74,  86, 100],
        [100,  86,  74,  62,  50,  36,  24,  12, 100,  86,  74,  62,  50,  36,  24,  12, 0  ],
        [  0,  25,  50,  75,  100, 75,  50,  25,   0,  25,  50,  75, 100,  75,  50,  25, 0  ],
        [100,  75,  50,  25,    0, 25,  50,  75, 100,  75,  50,  25,   0,  25,  50,  75, 100],
    ]
    accent_curves = [[128*x/100. for x in c] for c in accent_curves]
    scales = [
        'chromatic', 'major', 'harmonic_minor', 'melodic_minor', 'hex', 'aug', 'pentatonic_minor'
    ]
    styles = ['chord', 'updward', 'downward', 'converge', 'diverge', 'random']


    phrases = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    ]

    def __init__(
        self, channel=0,
        steps=16,
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
        repeat_time=16,  # this is the same as divsion, but for repeats, minimum is 1
        repeat_pace=None,  # supposed to accelerate or decelerate repeats - not implemented
        voicing=0,  # adds notes an octave above
        style=0,  # integer, picks
        melody=0,  # "depth" LFO for phrase (speed?)
        phrase=0,  # integer, picks phrase from a list
        scale=0,  # integer, picks scale from a list for phrase to operate on (default = chromatic)
        root=0,
        random=None,
        random_rate=None,
    ):
        self.channel = channel
        self.notes = [note_to_number(x) for x in notes or []]
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
        self.repeat_pace = repeat_pace
        self.melody = melody

        self.phrase = None
        self.accent_curve = None
        self.style = None
        self.scale = None

        self.accent_curve = self.accent_curves[accent_curve]
        self.style = self.styles[style]
        self.set_scale(scale, root=root)
        self.phrase = self.phrases[phrase]

        # require re-sequencing:

        self.sequence = []
        self.randoms = {}

        # some internal params
        self._sequence_start = None
        self._beat = None
        self._step = 1

        # for property getter/setters
        self.__steps = steps
        self.__bpm = None
        self.__pulses = pulses
        self.__voicing = voicing
        self.__voiced_notes = notes

    @property
    def pulses(self):
        return self.__pulses

    @pulses.setter
    def pulses(self, value):
        self.__pulses = value
        self.generate()

    @property
    def steps(self):
        return self.__steps

    @steps.setter
    def steps(self, value):
        self.__steps = value
        self.generate()

    @property
    def bpm(self):
        return self.__bpm

    @bpm.setter
    def bpm(self, value):
        self.__bpm = value
        self._beat = 60. / (value)

    @property
    def voicing(self):
        return self.__voicing

    @voicing.setter
    def voicing(self, value):
        self.__voiced_notes = self.notes
        ln = len(self.notes)
        for v in range(value):
            n = self.notes[v % ln]
            self.__voiced_notes.append(n + 12*(1+v//ln))

    @property
    def voiced_notes(self):
        return self.__voiced_notes

    def set_scale(self, value, root):
        self.scale = get_scale_numbers(root-root, scale_type=self.scales[value])

    def update_random(self, parameter, strength):
        if parameter not in self.randoms:
            self.randoms[parameter] = [0] * MAX_PULSE

        for i in range(MAX_PULSE):
            self.randoms[parameter][i] += random.randrange(-strength, strength)

    def generate(self):
        pulses = min(self.pulses, self.steps)
        interval = self.steps / pulses
        sequence = [0]*self.steps
        print(f"pulses={pulses} interval={interval} steps={self.steps} sequence={sequence}")

        for i in range(pulses):
            sequence[round(i*interval)] = 1

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

    def style_notes(self, index):
        return self.notes[index % len(self.notes)]

    def fill_lookahead(self, start, end):
        # not sure it's right to add delay in here...  if we only hve +ve delay we def don't
        # need to
        first_step = math.ceil(self.division*(start - self._sequence_start + self.delay*self._beat)/self._beat)
        last_step = math.floor(self.division*(end - self._sequence_start + self.delay*self._beat)/self._beat)

        if last_step < first_step:
            return []

        events = []
        for step in range(first_step, last_step+1):
            if not self.sequence[(step+self.rotate) % self.steps]:
                continue

            accent = (self.accent_curve[(step+self.rotate) % len(self.accent_curve)])*self.accent
            velocity = min(int(self.velocity + accent), 127)
            swing = 0 if step % 2 == 0 else (self.timing-0.5)
            vleft = (self.voicing+1+self.repeats) % (self.repeats+1)
            vmax = (vleft >= 0) + (self.voicing+1+self.repeats)//(self.repeats+1)

            notes = self.style_notes(0)
            for note in notes:
                melody_offset = None
#                if self.melody > 0:
#                    melody_offset = note + self.phrase[step]*self.melody
#                    # note = self.quantize(note + melody_offset)

                # do we want to step through accent curve, or apply it directly to sequence including
                # off notes?
                events.extend([
                    MidiEvent(
                        (step + swing + self.delay)*self._beat/self.division,
                        (NOTE_ON+self.channel, note+self.pitch, velocity)
                    ),
                    MidiEvent(
                        (step + self.sustain + self.delay)*self._beat/self.division,
                        (NOTE_OFF+self.channel, note+self.pitch, 0)
                    ),
                ])

            for r in range(1, self.repeats+1):
                notes = self.notes[self.style_notes(r)]
                vmax = (vleft >= r) + (self.voicing+1+self.repeats)//(self.repeats+1)
                for note in notes:
#                    if melody_offset:
#                        note = self.quantize(melody_offset)

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
    def __init__(self, midiout, interval=0.002, lookahead=.02, bpm=200):
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
        track.generate()

    def get_track(self, track_name, create=True):
        if track_name not in self.tracks and create:
            self.add_track(track_name, TorsoTrack())

        return self.tracks[track_name]

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def play_pause(self):
        if self._paused.is_set():
            print("play")
            self._paused.clear()
        else:
            print("pause")
            self._paused.set()

    def pause(self):
        self._paused.set()

    def fill_lookahead(self):
        next_lookahead = self._last_lookahead + self.lookahead
        for v in self.tracks.values():
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

