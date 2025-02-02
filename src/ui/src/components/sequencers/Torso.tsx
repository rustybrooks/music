import { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

import * as constants from './TorsoConstants';
import { keyMap, Mode } from './TorsoConstants';
import { MidiConfig, Settings } from '../MidiConfig';
import './Torso.css';
import { SequencerEvent, TorsoSequencer, TorsoTrack, TorsoTrackSlice } from '../../lib/sequencers/Torso';
import { note_to_number, NoteType, number_to_note } from '../../lib/Note';
import { ButtonState, TorsoButton } from './TorsoButton';
import { TorsoKnob } from './TorsoKnob';
import { scales } from '../../lib/sequencers/TorsoConstants';
import { MidiVisualizer } from '../displays/MidiVisualizer';
import { MidiContext } from '../../contexts/MidiContext';

function trackKey(bank: number, pattern: number, track: number) {
  return `${bank}:${pattern}:${track}`;
}

function getKnob(mode: Mode) {
  const r1 = constants.knobs[0].find(el => el.mode === mode || el.alt_mode === mode);
  const r2 = constants.knobs[1].find(el => el.mode === mode || el.alt_mode === mode);
  return r1 || r2;
}

function TorsoTable({
  sequencer,
  bank,
  pattern,
  track,
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  _foo,
}: {
  sequencer: TorsoSequencer;
  bank: number;
  pattern: number;
  track: number;
  _foo: any;
}) {
  const selectedTrack = sequencer.getTrack(trackKey(bank, pattern, track));
  return (
    <div style={{ minWidth: '15em', padding: '1em' }}>
      <table>
        <tbody>
          <tr>
            <td>Index</td>
            <td>
              {bank}:{pattern}:{track}
            </td>
            <td>BPM</td>
            <td>{sequencer.bpm}</td>
          </tr>
          <tr>
            <td>Steps</td>
            <td>{selectedTrack.getSteps()}</td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td>Pulses</td>
            <td>{selectedTrack.getPulses()}</td>
            <td>Rotate</td>
            <td>{selectedTrack.getRotate()}</td>
          </tr>
          <tr>
            <td>Cycles</td>
            <td></td>
            <td>Division</td>
            <td>{selectedTrack.division}</td>
          </tr>
          <tr>
            <td>Velocity</td>
            <td>{selectedTrack.velocity}</td>
            <td>Sustain</td>
            <td>{selectedTrack.sustain}</td>
          </tr>
          <tr>
            <td>Pitch</td>
            <td>{selectedTrack.pitch}</td>
            <td>Harmony</td>
            <td>{selectedTrack.harmony}</td>
          </tr>
          <tr>
            <td>Length</td>
            <td>{}</td>
            <td>Quantize</td>
            <td></td>
          </tr>
          <tr>
            <td>Repeats</td>
            <td>{selectedTrack.repeats}</td>
            <td>Offset</td>
            <td>{selectedTrack.repeatOffset}</td>
          </tr>
          <tr>
            <td>Time</td>
            <td>{selectedTrack.repeatTime}</td>
            <td>Pace</td>
            <td>{selectedTrack.repeatPace}</td>
          </tr>
          <tr>
            <td>Voicing</td>
            <td>{selectedTrack.getVoicing()}</td>
            <td>Style</td>
            <td>{selectedTrack.style.toString()}</td>
          </tr>
          <tr>
            <td>Melody</td>
            <td>{selectedTrack.melody}</td>
            <td>Phrase</td>
            <td>{selectedTrack.phrase}</td>
          </tr>
          <tr>
            <td>Accent</td>
            <td>{selectedTrack.accent}</td>
            <td>Accent Curve</td>
            <td>{selectedTrack.accentCurve}</td>
          </tr>
          <tr>
            <td>Timing</td>
            <td>{selectedTrack.timing}</td>
            <td>Delay</td>
            <td>{selectedTrack.delay}</td>
          </tr>
          <tr>
            <td>Scale</td>
            <td>{selectedTrack.getScale()}</td>
            <td>Root</td>
            <td>{selectedTrack.root}</td>
          </tr>
          <tr>
            <td>MIDI</td>
            <td>{selectedTrack.channel}</td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td>Random</td>
            <td>{selectedTrack.random}</td>
            <td>RRate</td>
            <td>{selectedTrack.random_rate}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export function Torso() {
  const hasPrevKeyPress = useRef<{ [id: string]: number | null }>({});
  const [modes, setModes] = useState([Mode.TRACKS]);
  const [control, setControl] = useState(false);
  const [track, setTrack] = useState(0);
  const [bank, setBank] = useState(0);
  const [pattern, setPattern] = useState(0);
  const [pitchOctave, setPitchOctave] = useState(3);
  const [visualizerCallback, setVisualizerCallback] = useState<(h: SequencerEvent[]) => void>(() => {});
  const [foo, setFoo] = useState(0);

  const { midiOutputs } = useContext(MidiContext);

  const [, setOutputs] = useState<number[]>([]);

  const buttonStates = [[...Array(13)].map(() => ButtonState.inactive), [...Array(13)].map(() => ButtonState.inactive)];
  const buttonText = [[...Array(13)].map(() => ''), [...Array(13)].map(() => '')];

  const mode = modes.slice(-1)[0];

  const visualizerCallbackCallback = useCallback((callback: any) => {
    setVisualizerCallback(() => callback);
  }, []);

  const addToHistory = useCallback(
    (h: SequencerEvent[]) => {
      if (visualizerCallback) visualizerCallback(h);
    },
    [visualizerCallback],
  );

  const sequencer = useMemo(() => {
    const s = new TorsoSequencer(null, addToHistory, 20);
    const slice1 = new TorsoTrackSlice({
      notes: [['C', 4] satisfies NoteType, ['E', 4] satisfies NoteType, ['G', 4] satisfies NoteType, ['B', 4] satisfies NoteType].map(
        (n: NoteType) => note_to_number(n),
      ),
      pulses: 8,
      steps: 16,
    });
    const slice2 = new TorsoTrackSlice({
      notes: [['A', 4] satisfies NoteType, ['C', 4] satisfies NoteType, ['E', 4] satisfies NoteType, ['G', 4] satisfies NoteType].map(
        (n: NoteType) => note_to_number(n),
      ),
      pulses: 8,
      steps: 16,
    });

    const ttrack = new TorsoTrack({
      output: null,
      slices: [slice1, slice2],
      repeats: 4,
      sustain: 0.5,
      style: 1,
      voicing: 1,
      repeatTime: 4,
      // timing: 8,
    });
    s.addTrack(trackKey(bank, pattern, track), ttrack);
    s.setBPM(10);
    setTimeout(() => s.run(), 1);
    return s;
  }, [visualizerCallback]);

  const interpolateSetValue = (value: any, interpolate: number | null = null): [keyof TorsoTrack | null, any] => {
    const knob = getKnob(mode);
    if (!knob) {
      console.log(`no map for mode=${mode}`);
      return [null, null];
    }

    if (control && !knob.alt_property) {
      console.log(`(set) No alt property for mode=${mode} knob=${JSON.stringify(knob, null, 2)}`);
      return [null, null];
    }

    const propKey = knob[control ? 'alt_set_property' : 'set_property'];
    if (!propKey) {
      console.log(`setValue - mode=${mode} no property`);
      return [null, null];
    }

    let lval;
    let fmin;
    let fmax;
    let ftype;
    if (!control && knob.list) {
      fmin = 0;
      fmax = knob.list.length - 1;
      ftype = 'int';
      // lval = knob.list;
    } else if (control && knob.alt_list) {
      fmin = 0;
      fmax = knob.alt_list.length - 1;
      ftype = 'int';
      // lval = knob.alt_list;
    } else if (control) {
      fmin = knob.alt_min || knob.min || 0;
      fmax = knob.alt_max || knob.max || 0;
      ftype = knob.alt_type || knob.type;
    } else {
      fmin = knob.min || 0;
      fmax = knob.max || 0;
      ftype = knob.type;
    }

    if (interpolate) {
      value = fmin + ((fmax - fmin) * value) / interpolate;
      if (ftype === 'int') {
        value = Math.round(value);
      }
    }

    if (lval) {
      return [propKey, lval[value]];
    }

    return [propKey, value];
  };

  const setValue = (value: any, interpolate: number | null = null) => {
    const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
    const [propKey, newValue] = interpolateSetValue(value, interpolate);
    if (propKey === 'bpm') {
      sequencer.setBPM(value);
    } else if (typeof ttrack[propKey as keyof TorsoTrack] === 'function') {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      ttrack[propKey](newValue);
    } else {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      ttrack[propKey] = newValue;
    }
  };

  const getValue = ({
    knob,
    interpolate = null,
    asInt = false,
    asIndex = true,
    useControl = null,
  }: {
    knob?: constants.Knob;
    interpolate?: number | null;
    asInt?: boolean;
    asIndex?: boolean;
    useControl?: boolean | null;
  } = {}) => {
    const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
    const thisKnob = knob || getKnob(mode);
    const thisControl = useControl != null ? useControl : control;

    if (!thisKnob) {
      console.log(`no map for mode=${mode}`);
      return null;
    }

    if (thisControl && !knob && !thisKnob.alt_property) {
      console.log(`(get) No alt property for mode=${mode} useControl=${useControl} knob=${JSON.stringify(thisKnob, null, 2)}`);
      return null;
    }

    const propKey = thisKnob[thisControl ? 'alt_property' : 'property'] as keyof TorsoTrack;
    // if (propKey === 'bpm') {
    //   return sequencer.bpm;
    // }

    let value;
    if (typeof ttrack[propKey] === 'function') {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignores
      value = ttrack[propKey]();
    } else {
      value = ttrack[propKey];
    }
    const lval = thisKnob[thisControl ? 'alt_list' : 'list'];
    let fmin = thisKnob.min ?? 0;
    let fmax = thisKnob.max ?? 0;

    if (lval) {
      fmin = 0;
      fmax = lval.length - 1;
    }

    if (interpolate) {
      value = (interpolate * ((value as number) - fmin)) / (fmax - fmin);
    }

    if (asInt || lval) {
      value = Math.round(value as number);
    }

    if (!asIndex && lval) {
      // console.log('!asindex', propKey, value, origValue, interpolate, thisKnob.min, thisKnob.max);
      value = lval[value as number];
    }

    return value;
  };

  const pushMode = (m: Mode, ma: Mode | null) => {
    let thisMode = m;
    if (control && ma) {
      thisMode = ma;
    }
    if (modes.includes(thisMode)) return;
    setModes([...modes, thisMode]);
  };

  const popMode = () => {
    setModes(modes.slice(0, modes.length - 1));
  };

  const buttonCommand = (row: number, col: number, press = false) => {
    const button = constants.buttons[row][col];
    let cmd = null;
    if (button.length > 3) {
      cmd = button[3][press ? 0 : 1];
    }

    if (cmd === 'play_pause') {
      sequencer.playPause();
    } else if (cmd === 'set_clear') {
      pushMode(Mode.CLEAR, Mode.COPY);
    } else if (cmd === 'set_control') {
      setControl(true);
    } else if (cmd === 'release_control') {
      setControl(false);
    } else if (cmd === 'set_bank') {
      pushMode(Mode.BANKS, Mode.SAVE);
    } else if (cmd === 'set_pattern') {
      pushMode(Mode.PATTERNS, Mode.SELECT);
    } else if (cmd === 'set_mute') {
      pushMode(Mode.MUTE, null);
    } else if (cmd === 'set_temp') {
      pushMode(Mode.TEMP, Mode.MULTI);
    } else if (cmd === 'release_mode') {
      popMode();
    }
  };

  const buttonPress = (row: number, col: number) => {
    const index = row * 8 + col;
    if (col < 8) {
      if ([Mode.TRACKS].includes(mode)) {
        setTrack(index);
      } else if ([Mode.PATTERNS].includes(mode)) {
        setPattern(index);
      } else if ([Mode.BANKS].includes(mode)) {
        setBank(index);
      } else if ([Mode.MUTE].includes(mode)) {
        const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
        ttrack.muted = !ttrack.muted;
      } else if ([Mode.PITCH].includes(mode)) {
        if (col === 7) {
          if (row === 0) {
            setPitchOctave(Math.min(pitchOctave + 1, 6));
          } else {
            setPitchOctave(Math.max(pitchOctave - 1, 0));
          }
        } else {
          const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
          const noteVals = ttrack.getNotes();
          const btext = buttonText[row][col];
          if (btext.length) {
            const n1 = btext.slice(0, -1);
            const n2 = parseInt(btext.slice(-1), 10);
            const note = note_to_number([n1, n2]);
            if (noteVals.includes(note)) {
              const ind = noteVals.indexOf(note);
              noteVals.splice(ind, 1);
            } else {
              noteVals.push(note);
            }
            ttrack.setNotes(noteVals);
            setFoo(foo + 1);
          }
        }
      } else if ([Mode.CHANNEL, Mode.ACCENT_CURVE, Mode.MELODY, Mode.PHRASE, Mode.STYLE].includes(mode)) {
        setValue(index);
      } else if (
        [
          Mode.STEPS,
          Mode.PULSES,
          Mode.ROTATE,
          Mode.REPEATS,
          Mode.REPEAT_OFFSET,
          Mode.VOICING,
          Mode.VELOCITY,
          Mode.SUSTAIN,
          Mode.REPEAT_PACE,
          Mode.MELODY,
          Mode.PHRASE,
          Mode.ACCENT,
          Mode.ACCENT_CURVE,
          Mode.ROOT,
          Mode.TIMING,
          Mode.DELAY,
          Mode.TEMPO,
        ].includes(mode)
      ) {
        setValue(index, constants.maxSteps);
      } else if ([Mode.SCALE].includes(mode)) {
        const imap: { [id: number]: string } = {
          8: 'chromatic',
          9: 'major',
          10: 'harmonic_minor',
          11: 'melodic_minor',
          12: 'hexatonic',
          13: 'augmented',
          14: 'pentatonic_minor',
        };
        if (index in imap) {
          setValue(scales.indexOf(imap[index]));
        }
      } else if ([Mode.DIVISION].includes(mode)) {
        // pass
      } else if ([Mode.MANUAL_STEPS].includes(mode)) {
        const steps = getValue();
        steps[index] = !steps[index];
      }
    } else {
      buttonCommand(row, col, true);
    }
  };

  const buttonRelease = (row: number, col: number) => {
    if (col >= 8) {
      buttonCommand(row, col, false);
    }
  };

  const pressKnob = (knob: constants.Knob) => {
    pushMode(knob.mode as Mode, knob.alt_mode as Mode);
  };

  const releaseKnob = (_knob: constants.Knob) => {
    popMode();
  };

  const rotateKnob = (_knob: constants.Knob, percent: number) => {
    setValue(percent, 100);
    setFoo(foo + 1);
  };

  const keyAction = (key: string, release: boolean) => {
    if (key in keyMap) {
      const x = keyMap[key];
      if (x[0] === 'knob') {
        const knob = constants.knobs[x[1]][x[2]];
        if (release) {
          releaseKnob(knob);
        } else {
          pressKnob(knob);
        }
      } else if (x[0] === 'button') {
        if (release) {
          buttonRelease(x[1], x[2]);
        } else {
          buttonPress(x[1], x[2]);
        }
      }
    } else if (key === 'Shift') {
      setControl(!release);
    }
  };

  const keyPress = (key: string) => {
    console.log('keypress', key);
    keyAction(key, false);
  };

  const keyRelease = (key: string) => {
    hasPrevKeyPress.current[key] = null;
    keyAction(key, true);
  };

  const keyPressRepeat = (key: string) => {
    if (!hasPrevKeyPress.current[key]) {
      keyPress(key);
      hasPrevKeyPress.current[key] = 1;
    }
  };

  const handleKeyDown = (event: KeyboardEvent): any => {
    keyPressRepeat(event.key);
  };

  const handleKeyUp = (event: KeyboardEvent): any => {
    keyRelease(event.key);
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown, false);
    window.addEventListener('keyup', handleKeyUp, false);

    // cleanup this component
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [handleKeyDown]);

  const settingsCallback = (settings: Settings) => {
    console.log(settings);
    setOutputs(settings.midiOutputs);
    sequencer.setOutput(settings.midiOutputs.length ? midiOutputs[settings.midiOutputs[0]] : null);
  };

  if (!sequencer) {
    return <div />;
  }

  if (!sequencer.paused) {
    buttonStates[0][9] = ButtonState.active;
  }
  if ([Mode.CLEAR, Mode.COPY].includes(mode)) {
    buttonStates[0][11] = ButtonState.active;
  }
  if (control) {
    buttonStates[0][12] = ButtonState.active;
  }
  if ([Mode.BANKS, Mode.SELECT].includes(mode)) {
    buttonStates[1][9] = ButtonState.active;
  }
  if ([Mode.PATTERNS, Mode.SAVE].includes(mode)) {
    buttonStates[1][10] = ButtonState.active;
  }
  if ([Mode.TEMP, Mode.MULTI].includes(mode)) {
    buttonStates[1][11] = ButtonState.active;
  }
  if ([Mode.MUTE].includes(mode)) {
    buttonStates[1][12] = ButtonState.active;
  }

  if ([Mode.TRACKS, Mode.MUTE].includes(mode)) {
    for (const rowStr of Object.keys(constants.buttons)) {
      const row = parseInt(rowStr, 10);
      for (const colStr of Object.keys(constants.buttons[row])) {
        const col = parseInt(colStr, 10);
        const index = row * 8 + col;
        const ttrack = sequencer.getTrack(trackKey(bank, pattern, index), false);
        if (index === track && col < 8) {
          buttonStates[row][col] = ButtonState.active;
        } else if (ttrack && !ttrack.muted) {
          buttonStates[row][col] = ButtonState.secondary;
        } else if (ttrack && ttrack.muted) {
          buttonStates[row][col] = ButtonState.passive;
        }
      }
    }
  } else if ([Mode.PATTERNS].includes(mode)) {
    const row = Math.floor(pattern / 8);
    const col = pattern % 8;
    buttonStates[row][col] = ButtonState.active;
  } else if ([Mode.BANKS].includes(mode)) {
    const row = Math.floor(bank / 8);
    const col = bank % 8;
    buttonStates[row][col] = ButtonState.active;
  } else if (
    [
      Mode.STEPS,
      Mode.VELOCITY,
      Mode.SUSTAIN,
      Mode.REPEATS,
      Mode.REPEAT_OFFSET,
      Mode.ACCENT,
      Mode.LENGTH,
      Mode.TIMING,
      Mode.DELAY,
      Mode.RANDOM,
      Mode.RANDOM_RATE,
      Mode.TEMPO,
    ].includes(mode)
  ) {
    const valueIndex = getValue({ interpolate: constants.maxSteps, asInt: true });
    for (const rowStr of Object.keys(constants.buttons)) {
      const row = parseInt(rowStr, 10);
      for (const colStr of Object.keys(constants.buttons[row])) {
        const col = parseInt(colStr, 10);
        const index = row * 8 + col;
        if (index <= valueIndex && col < 8) {
          buttonStates[row][col] = ButtonState.active;
        }
      }
    }
  } else if ([Mode.CHANNEL, Mode.ACCENT_CURVE, Mode.MELODY, Mode.PHRASE, Mode.STYLE, Mode.ROOT, Mode.VOICING, Mode.MELODY].includes(mode)) {
    const valueIndex = getValue({ interpolate: constants.maxSteps, asInt: true });
    for (const rowStr of Object.keys(constants.buttons)) {
      const row = parseInt(rowStr, 10);
      for (const colStr of Object.keys(constants.buttons[row])) {
        const col = parseInt(colStr, 10);
        const index = row * 8 + col;
        if (index === valueIndex && col < 8) {
          buttonStates[row][col] = ButtonState.active;
        }
      }
    }
  } else if ([Mode.SCALE].includes(mode)) {
    const dmap: { [id: string]: number[] } = {
      chromatic: [1, 0],
      major: [1, 1],
      harmonic_minor: [1, 2],
      melodic_minor: [1, 3],
      hexatonic: [1, 4],
      augmented: [1, 5],
      pentatonic_minor: [1, 6],
    };
    const valueIndex = getValue({ asIndex: false });
    // console.log('vindex', valueIndex);
    const [r, c] = dmap[valueIndex];
    for (const rowStr of Object.keys(constants.buttons)) {
      const row = parseInt(rowStr, 10);
      for (const colStr of Object.keys(constants.buttons[row])) {
        const col = parseInt(colStr, 10);
        if (row === r && col === c) buttonStates[row][col] = ButtonState.active;
      }
    }
  } else if ([Mode.DIVISION, Mode.REPEAT_TIME].includes(mode)) {
    const dmap: { [id: number]: number[] } = {
      1: [0, 0],
      2: [0, 1],
      4: [0, 2],
      8: [0, 3],
      16: [0, 4],
      32: [0, 5],
      64: [0, 6],
      3: [1, 2],
      6: [1, 3],
      12: [1, 4],
      24: [1, 5],
      48: [1, 6],
    };
    const valueIndex = getValue({ asIndex: false });
    const [r, c] = dmap[valueIndex];
    for (const rowStr of Object.keys(constants.buttons)) {
      const row = parseInt(rowStr, 10);
      for (const colStr of Object.keys(constants.buttons[row])) {
        const col = parseInt(colStr, 10);
        if (row === r && col === c) buttonStates[row][col] = ButtonState.active;
      }
    }
  } else if ([Mode.PULSES, Mode.ROTATE, Mode.MANUAL_STEPS].includes(mode)) {
    const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
    const seq = ttrack.getSequence();
    const man_knob = getKnob(Mode.MANUAL_STEPS);
    const man_steps = getValue({ knob: man_knob, useControl: true });
    for (const rowStr of Object.keys(constants.buttons)) {
      const row = parseInt(rowStr, 10);
      for (const colStr of Object.keys(constants.buttons[row])) {
        const col = parseInt(colStr, 10);
        const index = row * 8 + col;
        if (man_steps[(index - ttrack.getRotate()) % seq.length]) {
          buttonStates[row][col] = ButtonState.active;
        } else if (seq[(index - ttrack.getRotate()) % seq.length]) {
          buttonStates[row][col] = ButtonState.secondary;
        }
      }
    }
  } else if ([Mode.PITCH].includes(mode)) {
    const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
    const ourNotes = ttrack.getNotes();

    // white keys
    ['C', 'D', 'E', 'F', 'G', 'A', 'B'].forEach((n, i) => {
      const row = 1;
      const col = i;
      const this_n = note_to_number([n, n ? pitchOctave : 0]);
      buttonStates[row][col] = ourNotes.includes(this_n) ? ButtonState.whiteActive : ButtonState.whiteInactive;
      buttonText[row][col] = number_to_note(this_n).join('');
    });

    // black keys
    ['', 'C#', 'D#', '', 'F#', 'G#', 'A#'].forEach((n, i) => {
      const row = 0;
      const col = i;
      const this_n = note_to_number([n, n ? pitchOctave : 0]);
      if (n.length) {
        buttonStates[row][col] = ourNotes.includes(this_n) ? ButtonState.blackActive : ButtonState.blackInactive;
        buttonText[row][col] = number_to_note(this_n).join('');
      }
    });

    buttonStates[0][7] = ButtonState.secondary;
    buttonStates[1][7] = ButtonState.secondary;
  }

  return (
    <div style={{ display: 'flex' }}>
      <div style={{ display: 'inline-block', background: '#ddd', position: 'relative' }}>
        <MidiConfig settingsCallback={settingsCallback} />
        <table style={{ width: '100%' }}>
          <tbody>
            <tr>
              {constants.knobs[0].map((k, i) => (
                <td key={i}>
                  <TorsoKnob
                    k={k}
                    pressed={Boolean(
                      (control && k.alt_mode && k.alt_mode === modes[modes.length - 1]) ||
                        (!control && k.mode && k.mode === modes[modes.length - 1]),
                    )}
                    percent={getValue({ knob: k, interpolate: 100 })}
                    control={control}
                    pressCallback={() => pressKnob(k)}
                    releaseCallback={() => releaseKnob(k)}
                    rotateCallback={(p: number) => rotateKnob(k, p)}
                  />
                </td>
              ))}
            </tr>
            <tr>
              {constants.knobs[1].map((k, i) => (
                <td key={i}>
                  <TorsoKnob
                    k={k}
                    pressed={Boolean(
                      (control && k.alt_mode && k.alt_mode === modes[modes.length - 1]) ||
                        (!control && k.mode && k.mode === modes[modes.length - 1]),
                    )}
                    control={control}
                    percent={getValue({ knob: k, interpolate: 100 })}
                    pressCallback={() => pressKnob(k)}
                    releaseCallback={() => releaseKnob(k)}
                    rotateCallback={(p: number) => rotateKnob(k, p)}
                  />
                </td>
              ))}
            </tr>
          </tbody>
        </table>

        <table style={{ width: '100%', paddingLeft: '1rem' }}>
          <tbody>
            <tr>
              {constants.buttons[0].map((b, i) => (
                <td key={i}>
                  <TorsoButton
                    b={b}
                    row={0}
                    col={i}
                    onMouseDown={buttonPress}
                    onMouseUp={buttonRelease}
                    state={buttonStates[0][i]}
                    text={buttonText[0][i]}
                  />
                </td>
              ))}
            </tr>
            <tr>
              {constants.buttons[1].map((b, i) => (
                <td key={i}>
                  <TorsoButton
                    b={b}
                    row={1}
                    col={i}
                    onMouseDown={buttonPress}
                    onMouseUp={buttonRelease}
                    state={buttonStates[1][i]}
                    text={buttonText[1][i]}
                  />
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
      <TorsoTable bank={bank} pattern={pattern} track={track} sequencer={sequencer} _foo={foo} />
      <div style={{ minWidth: '20em', padding: '1em' }}>
        <MidiVisualizer callbackCallback={visualizerCallbackCallback} />
      </div>
    </div>
  );
}
