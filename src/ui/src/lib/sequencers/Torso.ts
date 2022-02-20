import { Heap } from 'heap-js';
import { accentCurves, NOTE_OFF, NOTE_ON, phrases, scales, styles } from './TorsoConstants';
import { getScaleNumbers } from '../Scales';
import { MidiOutput } from '../../types';
// import { MidiMessage } from '../../types';

const MAX_STEPS = 64;

class SequencerEvent {
  tick = 0;
  message: number[];
  output: MidiOutput;

  constructor(output: MidiOutput, tick: number, message: number[]) {
    this.output = output;
    this.tick = tick;
    this.message = message;
  }
}

class TrackSlice {
  steps: number;
  pulses: number;
  notes: number[];
  rotate: number;
  manual_steps: number[];
  sequence: number[] = [];

  constructor(steps = 16, pulses = 1, notes: number[] = [], rotate = 0, manual_steps: number[] = []) {
    this.steps = steps;
    this.pulses = pulses;
    this.notes = notes;
    this.rotate = rotate;
    this.manual_steps = [...manual_steps, ...[...Array(MAX_STEPS - manual_steps.length)].map(() => 0)];

    this.generate();
  }

  getSteps() {
    return this.steps;
  }

  setSteps(value: number) {
    this.steps = value;
    this.generate();
  }

  getPulses() {
    return this.pulses;
  }

  setPulses(value: number) {
    this.pulses = value;
    this.generate();
  }

  getManualSteps() {
    return this.manual_steps;
  }

  setManualSteps(value: number[]) {
    this.manual_steps = value;
    this.generate();
  }

  generate() {
    const pulses = Math.min(this.pulses, this.steps);
    const interval = Math.round(this.steps / pulses);
    const sequence = [...Array(this.steps)].map(() => 0);

    for (let i = 0; i < pulses; i += 1) {
      sequence[Math.round(i * interval)] = 1;
    }

    this.manual_steps.forEach((v, i) => {
      if (v < 0) {
        sequence[i] = 0;
      } else if (v > 0) {
        sequence[i] = v;
      }
    });

    this.sequence = sequence;
  }
}

class Track {
  output: MidiOutput;
  channel: number;
  slices: TrackSlice[];
  pitch: number;
  harmony: number;
  accent: number;
  accent_curve: number[];
  sustain: number;
  division: number;
  velocity: number;
  timing: number;
  delay: number;
  repeats: number;
  repeat_offset: number;
  repeat_time: number;
  repeat_pace: number;
  voicing: number;
  style: string;
  melody: number;
  phrase: number[];
  root: number;
  muted: boolean;

  slice_index = 0;
  slice_step = 0;
  bpm: number;
  scale_type: string | number;
  scale_notes: number[];
  track_name: string;
  sequenceStart: number = null;
  beat: number = null;
  step = 1;
  slice: TrackSlice = null;
  voiced_notes: number[];

  constructor({
    output,
    channel = 0,
    slices = null,
    pitch = 0, // pitch shift to apply to all notes, integer
    harmony = 0, // transpose notes defined in pitch up one at a time?
    accent = 0.5, // 0-1 the percent of accent curve to apply
    accent_curve = 0, // select from predefined accent curves
    sustain = 0.15, // Note length, in increments of step, i.e. 0.5 = half step
    division = 4, // how many pieces to divide a beat into
    velocity = 64, // base velocity - accent gets added to this
    timing = 0.5, // swing timing, 0.5=even, less means every other beat is early, more means late
    delay = 0, // delay pattern in relation to other patterns, +ve means later, in units of beat
    repeats = 0, // number of repeats to add, integer, will be is divisions of this.time
    repeat_offset = 0, // this delays the repeats, in units of 1 beat
    repeat_time = 1, // this is the same as divsion, but for repeats, minimum is 1
    repeat_pace = null, // supposed to accelerate or decelerate repeats - not implemented
    voicing = 0, // adds notes an octave above
    style = 0, // integer, picks
    melody = 0, // "depth" LFO for phrase (speed?)
    phrase = 0, // integer, picks phrase from a list
    scale = 0, // integer, picks scale from a list for phrase to operate on (default = chromatic)
    root = 0, // which note of the scale to set as the root
    muted = false,
  }: {
    output: MidiOutput;
    channel?: number;
    slices?: TrackSlice[];
    pitch?: number;
    harmony?: number;
    accent?: number;
    accent_curve?: number;
    sustain?: number;
    division?: number;
    velocity?: number;
    timing?: number;
    delay?: number;
    repeats?: number;
    repeat_offset?: number;
    repeat_time?: number;
    repeat_pace?: number;
    voicing?: number;
    style?: number;
    melody?: number;
    phrase?: number;
    scale?: string | number;
    root?: number;
    muted?: boolean;
  }) {
    Object.assign(this, {
      output,
      channel,
      pitch,
      harmony,
      accent,
      sustain,
      division,
      velocity,
      timing,
      delay,
      repeats,
      repeat_time,
      repeat_offset,
      repeat_pace,
      voicing,
      melody,
      phrase,
      root,
      muted,
    });

    this.scale_type = scale;
    this.slices = slices || [new TrackSlice()];
    this.accent_curve = accentCurves[accent_curve];
    this.style = styles[style];
    this.phrase = phrases[phrase];
  }

  addSlice(slice: TrackSlice) {
    this.slices.push(slice);
    if (this.slice === null) {
      this.setSlice(0);
    }
  }

  getScale() {
    return this.scale_type;
  }

  setScale(scale: string | number) {
    let scaleStr: string;
    if (typeof scale === 'number') {
      scaleStr = scales[scale];
    } else {
      scaleStr = scale;
    }
    this.scale_notes = getScaleNumbers(0, scaleStr, 10);
  }

  getSlice() {
    return this.slice;
  }

  setSlice(slice: number) {
    this.slice_index = slice;
    this.slice = this.slices[this.slice_index];
    this.setVoicing(this.voicing);
  }

  getNotes() {
    return this.slice.notes;
  }

  setNotes(value: number[]) {
    this.slice.notes = value;
  }

  getSteps() {
    return this.slice.steps;
  }

  setSteps(value: number) {
    this.slice.steps = value;
  }

  getPulses() {
    return this.slice.pulses;
  }

  setPulses(value: number) {
    this.slice.pulses = value;
  }

  getManualSteps() {
    return this.slice.manual_steps;
  }

  setManualSteps(value: number[]) {
    this.slice.manual_steps = value;
  }

  getRotate() {
    return this.slice.rotate;
  }

  setRotate(value: number) {
    this.slice.rotate = value;
  }

  getBPM() {
    return this.bpm;
  }

  setBPM(value: number) {
    this.bpm = value;
    this.beat = 60.0 / value;
  }

  getSequence() {
    return this.slice.sequence;
  }

  getVoicing() {
    return this.voicing;
  }

  setVoicing(value: number) {
    this.voicing = value;
    this.voiced_notes = [...this.slice.notes].sort();
    const ln = this.slice.notes.length;
    if (ln) {
      for (let v = 0; v < value; v += 1) {
        const n = this.slice.notes[v % ln];
        this.voiced_notes.push(n + 12 * (1 + Math.round(v / ln)));
      }
    }
  }

  getVoicedNotes() {
    return this.voiced_notes;
  }

  addNoteQuantized(note: number, offset: number) {
    const qnote = this.quantize(note);
    const notei = this.scale_notes.indexOf(qnote);
    return this.scale_notes[Math.round(notei + offset)];
  }

  quantize(note: number) {
    const overi = this.scale_notes.findIndex(n => n > note);
    const underi = overi - 1;

    let val: number;
    if (note - this.scale_notes[underi] < this.scale_notes[overi] - note) {
      val = this.scale_notes[underi + this.root];
    } else {
      val = this.scale_notes[overi + this.root];
    }
    return val;
  }

  styleNotes(index: number): number[] {
    const lv = this.voiced_notes.length;
    if (!lv) return [];

    if (this.style === 'chord') {
      return this.voiced_notes;
    }
    if (this.style === 'upward') {
      return [this.voiced_notes[index % lv]];
    }
    if (this.style === 'downward') {
      return [this.voiced_notes[lv - (index % lv) - 1]];
    }
    if (this.style === 'converge') {
      const i = index % lv;
      if (i % 2 === 0) {
        return [this.voiced_notes[Math.round(i / 2)]];
      }
      return [this.voiced_notes[lv - (Math.round(i / 2) + 1)]];
    }
    if (this.style === 'diverge') {
      const i = lv - (index % lv) - 1;
      if (i % 2 === 0) {
        return [this.voiced_notes[Math.round(i / 2)]];
      }
      return [this.voiced_notes[lv - (Math.round(i / 2) + 1)]];
    }
    if (this.style === 'alternate_bass') {
      const rest = this.voiced_notes.slice(1);
      const notes = [];
      for (const r of rest) {
        notes.push(this.voiced_notes[0]);
        notes.push(r);
      }
      return [notes[index]];
    }
    if (this.style === 'alternate_bass_2') {
      const rest = this.voiced_notes.slice(2);
      let i = 0;
      const notes = [];
      for (const r of rest) {
        notes.push(this.voiced_notes[i % 2]);
        notes.push(r);
        i += 1;
      }
      return [notes[index]];
    }
    if (this.style === 'alternate_melody') {
      const rest = this.voiced_notes.slice(0, lv - 1);
      const last = this.voiced_notes[lv - 1];
      const notes = [];
      for (const r of rest) {
        notes.push(r);
        notes.push(last);
      }
      return [notes[index]];
    }
    if (this.style === 'alternate_melody_2') {
      const rest = this.voiced_notes.slice(0, lv - 1);
      const last = this.voiced_notes.slice(lv - 2);
      const notes = [];
      let i = 0;
      for (const r of rest) {
        notes.push(r);
        notes.push(last[i % 2]);
        i += 1;
      }
      return [notes[index]];
    }
    if (this.style === 'random') {
      const num = Math.floor(Math.random() * lv) + 1;
      return [...Array(num)].map(() => this.voiced_notes[Math.floor(Math.random() * lv)]);
    }

    return [];
  }

  fillLookahead(start: number, end: number): any[] {
    const first_step = Math.ceil((this.division * (start - this.sequenceStart + this.delay * this.beat)) / this.beat);
    const last_step = Math.floor((this.division * (end - this.sequenceStart + this.delay * this.beat)) / this.beat);

    if (last_step < first_step) return [];
    const events = [];

    for (let step = first_step; step < last_step + 1; step += 1) {
      if (step === 0) {
        // this.random.update()
      }

      if (step - this.slice_step >= this.slice.steps) {
        this.setSlice((this.slice_index + 1) % this.slices.length);
      }

      if (!this.slice.sequence[(step - this.slice.rotate) % this.slice.steps]) {
        // eslint-disable-next-line no-continue
        continue;
      }

      const melody_offset = this.phrase[(step - this.slice.rotate) % this.phrase.length] * this.melody;
      const accent = this.accent_curve[(step - this.slice.rotate) % this.accent_curve.length] * this.accent;
      const velocity = Math.min(Math.round(this.velocity + accent), 127);
      const swing = step % 2 ? 0 : this.timing - 0.5;

      for (let r = 0; r < this.repeats; r += 1) {
        const notes: number[] = this.styleNotes(r);
        const melody_notes = notes.map(note => this.addNoteQuantized(note, melody_offset));
        for (const note of melody_notes) {
          events.push(
            new SequencerEvent(
              this.output,
              ((step + swing + this.delay + this.repeat_offset + r / this.repeat_time) * this.beat) / this.division,
              [NOTE_ON + this.channel, note + this.pitch, velocity],
            ),
            new SequencerEvent(
              this.output,
              ((step + this.sustain + this.delay + this.repeat_offset + r / this.repeat_time) * this.beat) / this.division,
              [NOTE_OFF + this.channel, note + this.pitch, 0],
            ),
          );
        }
      }
    }
    return events;
  }
}

export class Torso {
  output: MidiOutput;
  interval: number;
  lookahead: number;
  bpm: number;
  step = 0;

  start_time: number = null;
  tracks: { [id: string]: Track } = {};
  pending: SequencerEvent[] = [];
  last_lookahead: number = null;
  stopped = false;
  finished = false;
  paused = false;

  constructor(output: MidiOutput, interval = 3, lookahead = 10, bpm = 200) {
    this.output = output;
    this.interval = interval;
    this.lookahead = lookahead;
    this.bpm = bpm;

    // this.stopped = threading.Event();
    // this.finished = threading.Event();
    // this.paused = threading.Event();
  }

  setBPM(value: number) {
    Object.values(this.tracks).forEach(t => {
      t.setBPM(value);
    });
    this.bpm = value;
  }

  addTrack(track_name: string, track: Track) {
    this.tracks[track_name] = track;
    track.setBPM(this.bpm);
  }

  getTrack(track_name: string, create = true) {
    if (create && !(track_name in this.tracks)) {
      this.addTrack(track_name, new Track({ output: this.output }));
    }

    return this.tracks[track_name];
  }

  stop() {
    /*
        this._stopped.set()

        if this.is_alive():
            this._finished.wait(timeout)

        this.join()
     */
  }

  playPause() {
    /*
      if this._paused.is_set():
          this._paused.clear()
      else:
          this._paused.set()
    */
  }

  pause() {
    // this._paused.set()
  }

  fillLookahead() {
    if (this.last_lookahead === null) {
      this.last_lookahead = window.performance.now();
    }
    const next_lookahead = this.last_lookahead + this.lookahead;
    Object.values(this.tracks).forEach(track => {
      if (track.muted) {
        return;
      }

      const newvals = track.fillLookahead(this.last_lookahead, next_lookahead);
      if (newvals.length) {
        newvals.map((n: any) => Heap.heappush(this.pending, n));
      }

      this.last_lookahead = next_lookahead;
    });
  }

  reset() {
    this.step = 0;
    this.pending = [];
    this.start_time = window.performance.now();
    this.last_lookahead = this.start_time;
    Object.values(this.tracks).forEach(track => {
      track.sequenceStart = this.start_time;
    });

    this.fillLookahead();
    this.fillLookahead();
  }

  run() {
    this.reset();

    while (!this.stopped) {
      let reset = false;
      while (this.paused) {
        // sleep .2s
        reset = true;
      }
      if (reset) this.reset();

      const t1 = window.performance.now();
      const t1o = t1 - this.start_time;
      const due: SequencerEvent[] = [];
      while (true) {
        if (!this.pending.length || this.pending[0].tick > t1o) {
          break;
        }
        const evt = Heap.heappop(this.pending);
        Heap.heappush(due, evt);
      }

      if (due.length) {
        for (let i = 0; i < due.length; i += 1) {
          const evt = Heap.heappop(due);
          this.output.object.send(evt.message, evt.tick);
        }
      }

      if (t1 >= this.last_lookahead) {
        this.fillLookahead();
        // eslint-disable-next-line no-continue
        continue;
      }

      this.step += 1;
      const left = this.interval * this.step - (window.performance.now() - this.start_time);
      if (left <= 0) {
        console.log('overflow time');
      } else {
        setTimeout(this.run, left);
      }
    }

    // this.finished.set
  }
}
