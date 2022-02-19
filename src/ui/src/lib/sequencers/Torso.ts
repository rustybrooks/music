import { Heap } from 'heap-js';
// import { MidiMessage } from '../../types';

const MAX_STEPS = 64;

class SequencerEvent {
  tick = 0;
  message: any;
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
  bpm: number;
  muted = false;
  sequenceStart: Date = null;

  setBPM(value: number) {
    this.bpm = value;
  }

  fillLookahead(last: Date, next: Date): any[] {
    return [];
  }
}

export class Torso {
  interval: number;
  lookahead: number;
  bpm: number;
  step = 0;

  start_time: Date = null;
  tracks: { [id: string]: Track } = {};
  pending: SequencerEvent[] = [];
  last_lookahead: Date = null;
  stopped = false;
  finished = false;
  paused = false;

  constructor(interval = 0.003, lookahead = 0.01, bpm = 200) {
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
      this.addTrack(track_name, new Track());
    }

    return this.tracks[track_name];
  }

  stop() {
    /*
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()
     */
  }

  playPause() {
    /*
      if self._paused.is_set():
          self._paused.clear()
      else:
          self._paused.set()
    */
  }

  pause() {
    // self._paused.set()
  }

  fillLookahead() {
    const next_lookahead = new Date(this.last_lookahead);
    next_lookahead.setSeconds(next_lookahead.getSeconds() + this.lookahead);
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
    this.start_time = new Date();
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

      const t1 = new Date();
      const t1o = t1.getTime() / 1000.0 - this.start_time.getTime() / 1000.0;
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
          // sendmessage evt
        }
      }

      if (t1 >= this.last_lookahead) {
        this.fillLookahead();
        // eslint-disable-next-line no-continue
        continue;
      }

      this.step += 1;
      const left = this.interval * this.step - (new Date().getTime() / 1000.0 - this.start_time.getTime() / 1000.0);
      if (left <= 0) {
        console.log('overflow time');
      } else {
        // sleep(left)
      }
    }

    // this.finished.set
  }
}
