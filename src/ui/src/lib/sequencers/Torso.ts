import { Heap } from 'heap-js';
import { accentCurves, NOTE_OFF, NOTE_ON, phrases, scales, styles } from './TorsoConstants';
import { getScaleNumbers } from '../Scales';
import { MidiOutput } from '../../types';
import { sleep } from '../utils';
import { synthMidiMessage } from '../synthesizers/Basic';
// import { MidiMessage } from '../../types';

const MAX_STEPS = 64;

let sequencerId = 0;

class SequencerEvent {
  tick = 0;
  message: number[];
  output: MidiOutput;
  id: number;

  constructor(output: MidiOutput, tick: number, message: number[]) {
    this.output = output;
    this.tick = tick;
    this.message = message;
    this.id = sequencerId;
    // console.log('new msg', this.tick, this.message, this.id, this.output);
    sequencerId += 1;
  }
}

function SequencerComparator(a: SequencerEvent, b: SequencerEvent) {
  if (a.tick > b.tick) {
    return 1;
  }
  if (a.tick === b.tick) {
    return 0;
  }
  return -1;
}

export class TorsoTrackSlice {
  steps: number;
  pulses: number;
  notes: number[];
  rotate: number;
  manualSteps: number[];
  sequence: number[] = [];

  constructor({
    steps = 16,
    pulses = 1,
    notes = [],
    rotate = 0,
    manualSteps = [],
  }: {
    steps?: number;
    pulses?: number;
    notes?: number[];
    rotate?: number;
    manualSteps?: number[];
  }) {
    Object.assign(this, { steps, pulses, notes, rotate });
    this.manualSteps = [...manualSteps, ...[...Array(MAX_STEPS - manualSteps.length)].map(() => 0)];
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
    return this.manualSteps;
  }

  setManualSteps(value: number[]) {
    this.manualSteps = value;
    this.generate();
  }

  generate() {
    const pulses = Math.min(this.pulses, this.steps);
    const interval = Math.round(this.steps / pulses);
    const sequence = [...Array(this.steps)].map(() => 0);

    for (let i = 0; i < pulses; i += 1) {
      sequence[Math.round(i * interval)] = 1;
    }

    this.manualSteps.forEach((v, i) => {
      if (v < 0) {
        sequence[i] = 0;
      } else if (v > 0) {
        sequence[i] = v;
      }
    });

    this.sequence = sequence;
  }
}

export class TorsoTrack {
  output: MidiOutput;
  channel: number;
  slices: TorsoTrackSlice[];
  pitch: number;
  harmony: number;
  accent: number;
  accentCurve: number[];
  sustain: number;
  division: number;
  velocity: number;
  timing: number;
  delay: number;
  repeats: number;
  repeatOffset: number;
  repeatTime: number;
  repeatPace: number;
  voicing: number;
  style: string;
  melody: number;
  phrase: number[];
  root: number;
  muted: boolean;

  sliceIndex = 0;
  sliceStep = 0;
  lastStep = -1;
  bpm: number;
  scaleType: string | number;
  scaleNotes: number[];
  trackName: string;
  sequenceStart: number = null;
  beat: number = null;
  slice: TorsoTrackSlice = null;
  voicedNotes: number[];

  constructor({
    output,
    channel = 0,
    slices = null,
    pitch = 0, // pitch shift to apply to all notes, integer
    harmony = 0, // transpose notes defined in pitch up one at a time?
    accent = 0.5, // 0-1 the percent of accent curve to apply
    accentCurve = 0, // select from predefined accent curves
    sustain = 0.15, // Note length, in increments of step, i.e. 0.5 = half step
    division = 4, // how many pieces to divide a beat into
    velocity = 64, // base velocity - accent gets added to this
    timing = 0.5, // swing timing, 0.5=even, less means every other beat is early, more means late
    delay = 0, // delay pattern in relation to other patterns, +ve means later, in units of beat
    repeats = 0, // number of repeats to add, integer, will be is divisions of this.time
    repeatOffset = 0, // this delays the repeats, in units of 1 beat
    repeatTime = 1, // this is the same as divsion, but for repeats, minimum is 1
    repeatPace = null, // supposed to accelerate or decelerate repeats - not implemented
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
    slices?: TorsoTrackSlice[];
    pitch?: number;
    harmony?: number;
    accent?: number;
    accentCurve?: number;
    sustain?: number;
    division?: number;
    velocity?: number;
    timing?: number;
    delay?: number;
    repeats?: number;
    repeatOffset?: number;
    repeatTime?: number;
    repeatPace?: number;
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
      repeatTime,
      repeatOffset,
      repeatPace,
      voicing,
      melody,
      phrase,
      root,
      muted,
    });

    this.scaleType = scale;
    this.slices = slices || [new TorsoTrackSlice({})];
    this.accentCurve = accentCurves[accentCurve];
    this.style = styles[style];
    this.phrase = phrases[phrase];

    this.setSlice(0);
    this.setScale(this.scaleType);
  }

  setOutput(output: MidiOutput) {
    this.output = output;
  }

  addSlice(slice: TorsoTrackSlice) {
    this.slices.push(slice);
    if (this.slice === null) {
      this.setSlice(0);
    }
  }

  getScale() {
    return this.scaleType;
  }

  setScale(scale: string | number) {
    let scaleStr: string;
    if (typeof scale === 'number') {
      scaleStr = scales[scale];
    } else {
      scaleStr = scale;
    }
    this.scaleNotes = getScaleNumbers(0, scaleStr, 10);
  }

  getSlice() {
    return this.slice;
  }

  setSlice(slice: number) {
    this.sliceIndex = slice;
    this.slice = this.slices[this.sliceIndex];
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
    return this.slice.manualSteps;
  }

  setManualSteps(value: number[]) {
    this.slice.manualSteps = value;
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
    this.beat = (1000 * 60.0) / value;
  }

  getSequence() {
    return this.slice.sequence;
  }

  getVoicing() {
    return this.voicing;
  }

  setVoicing(value: number) {
    this.voicing = value;
    this.voicedNotes = [...this.slice.notes].sort();
    const ln = this.slice.notes.length;
    if (ln) {
      for (let v = 0; v < value; v += 1) {
        const n = this.slice.notes[v % ln];
        this.voicedNotes.push(n + 12 * (1 + Math.round(v / ln)));
      }
    }
  }

  getVoicedNotes() {
    return this.voicedNotes;
  }

  addNoteQuantized(note: number, offset: number) {
    const qnote = this.quantize(note);
    const notei = this.scaleNotes.indexOf(qnote);
    return this.scaleNotes[Math.round(notei + offset)];
  }

  quantize(note: number) {
    const overi = this.scaleNotes.findIndex(n => n > note);
    const underi = overi - 1;

    let val: number;
    if (note - this.scaleNotes[underi] < this.scaleNotes[overi] - note) {
      val = this.scaleNotes[underi + this.root];
    } else {
      val = this.scaleNotes[overi + this.root];
    }
    return val;
  }

  styleNotes(index: number): number[] {
    const lv = this.voicedNotes.length;
    if (!lv) return [];

    if (this.style === 'chord') {
      return this.voicedNotes;
    }
    if (this.style === 'upward') {
      return [this.voicedNotes[index % lv]];
    }
    if (this.style === 'downward') {
      return [this.voicedNotes[lv - (index % lv) - 1]];
    }
    if (this.style === 'converge') {
      const i = index % lv;
      if (i % 2 === 0) {
        return [this.voicedNotes[Math.round(i / 2)]];
      }
      return [this.voicedNotes[lv - (Math.round(i / 2) + 1)]];
    }
    if (this.style === 'diverge') {
      const i = lv - (index % lv) - 1;
      if (i % 2 === 0) {
        return [this.voicedNotes[Math.round(i / 2)]];
      }
      return [this.voicedNotes[lv - (Math.round(i / 2) + 1)]];
    }
    if (this.style === 'alternate_bass') {
      const rest = this.voicedNotes.slice(1);
      const notes = [];
      for (const r of rest) {
        notes.push(this.voicedNotes[0]);
        notes.push(r);
      }
      return [notes[index]];
    }
    if (this.style === 'alternate_bass_2') {
      const rest = this.voicedNotes.slice(2);
      let i = 0;
      const notes = [];
      for (const r of rest) {
        notes.push(this.voicedNotes[i % 2]);
        notes.push(r);
        i += 1;
      }
      return [notes[index]];
    }
    if (this.style === 'alternate_melody') {
      const rest = this.voicedNotes.slice(0, lv - 1);
      const last = this.voicedNotes[lv - 1];
      const notes = [];
      for (const r of rest) {
        notes.push(r);
        notes.push(last);
      }
      return [notes[index]];
    }
    if (this.style === 'alternate_melody_2') {
      const rest = this.voicedNotes.slice(0, lv - 1);
      const last = this.voicedNotes.slice(lv - 2);
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
      return [...Array(num)].map(() => this.voicedNotes[Math.floor(Math.random() * lv)]);
    }

    return [];
  }

  fillLookahead(start: number, end: number): any[] {
    const firstStep = Math.max(
      Math.ceil((this.division * (start - this.sequenceStart + this.delay * this.beat)) / this.beat),
      this.lastStep + 1,
    );
    const lastStep = Math.floor((this.division * (end - this.sequenceStart + this.delay * this.beat)) / this.beat);
    console.log(start, end, firstStep, lastStep, this.lastStep);
    if (lastStep < firstStep) return [];
    this.lastStep = lastStep;
    const events = [];

    for (let step = firstStep; step <= lastStep; step += 1) {
      if (step === 0) {
        // this.random.update()
      }

      if (step - this.sliceStep >= this.slice.steps) {
        console.log('next slice', this.lastStep, step);
        this.sliceStep = step;
        this.setSlice((this.sliceIndex + 1) % this.slices.length);
      }

      if (!this.slice.sequence[(step - this.slice.rotate) % this.slice.steps]) {
        // eslint-disable-next-line no-continue
        continue;
      }

      const melodyOffset = this.phrase[(step - this.slice.rotate) % this.phrase.length] * this.melody;
      const accent = this.accentCurve[(step - this.slice.rotate) % this.accentCurve.length] * this.accent;
      const velocity = Math.min(Math.round(this.velocity + accent), 127);
      const swing = step % 2 ? 0 : this.timing - 0.5;

      for (let r = 0; r < this.repeats + 1; r += 1) {
        const notes: number[] = this.styleNotes(r);
        const melodyNotes = notes.map(note => this.addNoteQuantized(note, melodyOffset));
        for (const note of melodyNotes) {
          events.push(
            new SequencerEvent(
              this.output,
              ((step + swing + this.delay + this.repeatOffset + r / this.repeatTime) * this.beat) / this.division,
              [NOTE_ON + this.channel, note + this.pitch, velocity],
            ),
            new SequencerEvent(
              this.output,
              ((step + this.sustain + this.delay + this.repeatOffset + r / this.repeatTime) * this.beat) / this.division,
              [NOTE_OFF + this.channel, note + this.pitch, 0],
            ),
          );
        }
      }
    }
    console.log('return', events.length);
    return events;
  }
}

export class TorsoSequencer {
  messageCallback: (message: string) => void;
  output: MidiOutput;
  interval: number;
  lookahead: number;
  bpm: number;
  step = 0;

  startTime: number = null;
  tracks: { [id: string]: TorsoTrack } = {};
  pending = new Heap(SequencerComparator);
  lastLookahead: number = null;
  stopped = false;
  finished = false;
  paused = true;

  constructor(output: MidiOutput = null, messageCallback: (message: string) => void = null, interval = 20, lookahead = 40, bpm = 200) {
    this.output = output;
    this.messageCallback = messageCallback;
    this.interval = interval;
    this.lookahead = lookahead;
    this.bpm = bpm;
  }

  setOutput(output: MidiOutput) {
    Object.values(this.tracks).forEach(t => {
      t.setOutput(output);
    });
    this.output = output;
  }

  setBPM(value: number) {
    Object.values(this.tracks).forEach(t => {
      t.setBPM(value);
    });
    this.bpm = value;
  }

  addTrack(trackName: string, track: TorsoTrack) {
    this.tracks[trackName] = track;
    track.setBPM(this.bpm);
  }

  getTrack(trackName: string, create = true) {
    if (create && !(trackName in this.tracks)) {
      console.log('addTrack', trackName);
      this.addTrack(trackName, new TorsoTrack({ output: this.output }));
    }

    return this.tracks[trackName];
  }

  stop() {
    this.stopped = true;
  }

  playPause() {
    this.paused = !this.paused;
    console.log('playpause', this.paused);
  }

  pause() {
    this.paused = true;
  }

  fillLookahead() {
    if (this.lastLookahead === null) {
      this.lastLookahead = window.performance.now();
    }
    const nextLookahead = this.lastLookahead + this.lookahead;
    Object.values(this.tracks).forEach(track => {
      if (track.muted) {
        return;
      }

      const newvals = track.fillLookahead(this.lastLookahead, nextLookahead);
      if (newvals.length) {
        newvals.forEach((n: any) => {
          this.pending.push(n);
          // console.log('push pending', n, this.pending.length);
        });
      }

      this.lastLookahead = nextLookahead;
    });
  }

  reset() {
    this.step = 0;
    this.pending = new Heap(SequencerComparator);
    this.startTime = window.performance.now();
    this.lastLookahead = this.startTime;
    Object.values(this.tracks).forEach(track => {
      track.sequenceStart = this.startTime;
    });

    this.fillLookahead();
    this.fillLookahead();
  }

  async run() {
    this.reset();

    while (!this.stopped) {
      // const firstLeft = this.interval * this.step - (window.performance.now() - this.start_time);
      let reset = false;
      while (this.paused) {
        await sleep(200);
        reset = true;
      }
      if (reset) this.reset();

      const t1 = window.performance.now();
      const t1o = t1 - this.startTime;
      while (true) {
        if (!this.pending.length || this.pending.peek().tick > t1o) {
          break;
        }
        const evt = this.pending.pop();
        console.log('send', evt);
        this.messageCallback(`${evt.message} ${evt.tick}`);
        if (evt.output) {
          evt.output.object.send(evt.message, evt.tick);
        } else {
          synthMidiMessage(evt.message, evt.tick);
        }
      }

      if (t1 >= this.lastLookahead) {
        this.fillLookahead();
        // eslint-disable-next-line no-continue
        continue;
      }

      this.step += 1;
      const left = this.interval * this.step - (window.performance.now() - this.startTime);
      if (left < 0) {
        // console.log('overflow time', left);
      } else {
        // console.log('sleep', left, firstLeft);
        await sleep(left);
        // setTimeout(this.run, left);
      }
    }

    // this.finished.set
  }
}
