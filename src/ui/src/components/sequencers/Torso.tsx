import { useGetAndSet } from 'react-context-hook';
import { useEffect, useMemo, useRef, useState } from 'react';

import { isFunction } from 'webpack-merge/dist/utils';
import * as constants from './TorsoConstants';
import { keyMap, Mode } from './TorsoConstants';
import { MidiConfig, Settings } from '../MidiConfig';
import { MidiOutputs } from '../../types';
import './Torso.css';
import { TorsoSequencer, TorsoTrack, TorsoTrackSlice } from '../../lib/sequencers/Torso';
import { note_to_number, NoteType } from '../../lib/Note';
import { Button, ButtonState } from './TorsoButton';
import { Knob } from './TorsoKnob';

function trackKey(bank: number, pattern: number, track: number) {
  return `${bank}:${pattern}:${track}`;
}

function getKnob(mode: Mode) {
  const r1 = constants.knobs[0].find(el => el.mode === mode || el.alt_mode === mode);
  const r2 = constants.knobs[1].find(el => el.mode === mode || el.alt_mode === mode);
  return r1 || r2;
}

export function Torso() {
  const hasPrevKeyPress = useRef<{ [id: string]: number }>({});
  const [modes, setModes] = useState([Mode.TRACKS]);
  const [control, setControl] = useState(false);
  const [track, setTrack] = useState(0);
  const [bank, setBank] = useState(0);
  const [pattern, setPattern] = useState(0);
  const [foo, setFoo] = useState(0);

  // const [midiCallbackMap, setMidiCallbackMap] = useGetAndSet<CallbackMap>('midiCallbackMap');
  // const [midiInputs, setMidiInputs] = useGetAndSet<MidiInputs>('midiInputs');
  const [midiOutputs] = useGetAndSet<MidiOutputs>('midiOutputs');
  // const [midiAccess, setMidiAccess] = useGetAndSet<WebMidi.MIDIAccess>('midiAccess');
  const [, setOutputs] = useState([]);

  const mode = modes.slice(-1)[0];

  const sequencer = useMemo(() => {
    const s = new TorsoSequencer();
    const slice = new TorsoTrackSlice({
      notes: [
        ['C', 4],
        ['E', 4],
        ['G', 4],
        ['B', 4],
      ].map((n: NoteType) => note_to_number(n)),
      pulses: 16,
      steps: 16,
    });
    const ttrack = new TorsoTrack({
      output: null,
      slices: [slice],
      repeats: 2,
      sustain: 1,
      style: 1,
      voicing: 3,
    });
    s.addTrack('1', ttrack);
    s.run();
    return s;
  }, []);

  const interpolateSetValue = (value: any, interpolate: number = null): [keyof TorsoTrack, any] => {
    const knob = getKnob(mode);
    if (!knob) {
      console.log(`no map for mode=${mode}`);
      return null;
    }

    if (!knob.alt_property) {
      console.log(`No alt property for mode=${mode}`);
      return [null, null];
    }

    const propKey = knob[control ? 'alt_property' : 'property'];
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
      lval = knob.list;
    } else if (control && knob.alt_list) {
      fmin = 0;
      fmax = knob.alt_list.length - 1;
      ftype = 'int';
      lval = knob.alt_list;
    } else if (control) {
      fmin = knob.alt_min || knob.min;
      fmax = knob.alt_max || knob.max;
      ftype = knob.alt_type || knob.type;
    } else {
      fmin = knob.min;
      fmax = knob.max;
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

  const setValue = (value: any, interpolate: number = null) => {
    const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
    const [propKey, newValue] = interpolateSetValue(value, interpolate);
    if (propKey === 'bpm') {
      sequencer.setBPM(value);
    } else if (isFunction(propKey)) {
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
    interpolate?: number;
    asInt?: boolean;
    asIndex?: boolean;
    useControl?: boolean;
  }) => {
    const ttrack = sequencer.getTrack(trackKey(bank, pattern, track));
    const thisKnob = knob || getKnob(mode);
    const thisControl = useControl != null ? useControl : control;

    if (!thisKnob) {
      console.log(`no map for mode=${mode}`);
      return null;
    }

    if (thisControl && !thisKnob.alt_property) {
      console.log(`No alt property for mode=${mode}`);
      return null;
    }

    const propKey = thisKnob[thisControl ? 'alt_property' : 'property'];
    // if (propKey === 'bpm') {
    //   return sequencer.bpm;
    // }

    let value;
    if (isFunction(ttrack[propKey])) {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      value = ttrack[propKey]();
    } else {
      value = ttrack[propKey];
    }

    const lval = thisKnob[thisControl ? 'alt_list' : 'list'];
    if (asIndex && lval) {
      value = lval.indexOf(value);
    }

    if (interpolate) {
      value = (interpolate * (value - thisKnob.min)) / (thisKnob.max - thisKnob.min);
    }

    if (asInt) {
      value = Math.round(value);
    }

    return value;
  };

  const buttonPress = (row: number, col: number) => {};

  const pushMode = (m: Mode) => {
    setModes([...modes, m]);
  };

  const popMode = () => {
    setModes(modes.slice(0, modes.length - 1));
  };

  const pressKnob = (knob: constants.Knob) => {
    if (control) {
      if (knob.alt_mode) {
        pushMode(knob.alt_mode);
      }
    } else {
      pushMode(knob.mode);
    }
  };

  const releaseKnob = (knob: constants.Knob) => {
    popMode();
  };

  const rotateKnob = (knob: constants.Knob, percent: number) => {
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
      }
    } else if (key === 'Control') {
      setControl(!release);
    }
  };

  const keyPress = (key: string) => {
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
    setOutputs(settings.midiOutputs);
    sequencer.output = settings.midiOutputs.length ? midiOutputs[settings.midiOutputs[0]] : null;
  };

  if (!sequencer) {
    return <div />;
  }

  const buttonStates = [[...Array(13)].map(() => ButtonState.inactive), [...Array(13)].map(() => ButtonState.inactive)];
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
  } else if ([Mode.BANKS].includes(mode)) {
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
  } else if ([Mode.SCALE].includes(mode)) {
  } else if ([Mode.DIVISION, Mode.REPEAT_TIME].includes(mode)) {
  } else if ([Mode.PULSES, Mode.ROTATE, Mode.MANUAL_STEPS].includes(mode)) {
  } else if ([Mode.PITCH].includes(mode)) {
  }

  return (
    <div style={{ display: 'inline-block', background: '#ddd', position: 'relative' }}>
      <MidiConfig settingsCallback={settingsCallback} />
      <table style={{ width: '100%' }}>
        <tbody>
          <tr>
            {constants.knobs[0].map((k, i) => (
              <td key={i}>
                <Knob
                  k={k}
                  pressed={
                    (control && k.alt_mode && k.alt_mode === modes[modes.length - 1]) ||
                    (!control && k.mode && k.mode === modes[modes.length - 1])
                  }
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
                <Knob
                  k={k}
                  pressed={
                    (control && k.alt_mode && k.alt_mode === modes[modes.length - 1]) ||
                    (!control && k.mode && k.mode === modes[modes.length - 1])
                  }
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
                <Button b={b} row={0} col={i} onClick={buttonPress} state={buttonStates[0][i]} />
              </td>
            ))}
          </tr>
          <tr>
            {constants.buttons[1].map((b, i) => (
              <td key={i}>
                <Button b={b} row={1} col={i} onClick={buttonPress} state={buttonStates[1][i]} />
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
