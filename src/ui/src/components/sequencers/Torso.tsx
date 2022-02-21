import { useGetAndSet } from 'react-context-hook';

import * as constants from './TorsoConstants';
import { MidiConfig, Settings } from '../MidiConfig';
import { CallbackMap, MidiInputs, MidiOutputs } from '../../types';
import './Torso.css';
import { useEffect, useRef, useState } from 'react';
import { TorsoSequencer, TorsoTrack, TorsoTrackSlice } from '../../lib/sequencers/Torso';
import { note_to_number, NoteType } from '../../lib/Note';
import { keyMap, knobs, Mode } from './TorsoConstants';

enum ButtonState {
  inactive,
  active,
  secondary,
}

function Knob({ k, pressed, control }: { k: any; pressed: boolean; control: boolean }) {
  const colors = {
    normal: '#aa6666',
    pressed: '#aaaa66',
    control: '#aa66aa',
  };
  let color = colors.normal;
  if (pressed) {
    color = control ? colors.control : colors.pressed;
  }
  return (
    <div style={{ textAlign: 'center', padding: '.4rem' }}>
      <svg width="4rem" height="4rem" viewBox="0 0 20 20" version="1.1" transform="rotate(0)">
        <circle fill={colors.normal} fillRule="evenodd" stroke="#a10000" strokeWidth=".5" strokeOpacity="1" cx="10" cy="10" r="9" />
        <circle fill={color} fillRule="evenodd" cx="10" cy="10" r="4" />
        <circle fill="#000000" cx="10" cy="4" r="2" />
        <text alignmentBaseline="middle" textAnchor="middle" x="10" y="10" className="knob">
          {k.keybind}
        </text>
      </svg>{' '}
      <div style={{ fontSize: '.8rem' }}>{k.label}</div>
      <div style={{ fontSize: '.8rem' }}>{k.alt_label}&nbsp;</div>
    </div>
  );
}

function Button({
  b,
  onClick,
  row,
  col,
  state,
}: {
  b: any;
  row: number;
  col: number;
  onClick?: (r: number, c: number) => void;
  state: ButtonState;
}) {
  return (
    <div className="torso-button" onClick={() => onClick(row, col)}>
      <svg width="4rem" height="4rem" viewBox="0 0 20 20" version="1.1" style={{ margin: 0, padding: 0 }}>
        <rect fill="#999" width="15.5" height="15.5" x="0.25" y="0.25" stroke="#666" strokeWidth=".5" strokeOpacity="1" />
        <text alignmentBaseline="middle" textAnchor="middle" x="8" y="8" className="button-label">
          {b[2]}
        </text>
        <text x="2" y="19.25" className="button-bot">
          {b[0]}
        </text>
        <text alignmentBaseline="middle" transform="rotate(-90) translate(-11, 17.5)" className="button-side">
          {b[1]}
        </text>
      </svg>
    </div>
  );
}

export function Torso() {
  let sequencer: TorsoSequencer;
  const hasPrevKeyPress = useRef<{ [id: string]: number }>({});
  const [modes, setModes] = useState([Mode.TRACKS]);
  const [control, setControl] = useState(false);

  const [midiCallbackMap, setMidiCallbackMap] = useGetAndSet<CallbackMap>('midiCallbackMap');
  const [midiInputs, setMidiInputs] = useGetAndSet<MidiInputs>('midiInputs');
  const [midiOutputs, setMidiOutputs] = useGetAndSet<MidiOutputs>('midiOutputs');
  const [midiAccess, setMidiAccess] = useGetAndSet<WebMidi.MIDIAccess>('midiAccess');
  const [outputs, setOutputs] = useState([]);

  console.log('render', modes);

  useEffect(() => {
    sequencer = new TorsoSequencer();
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
    const track = new TorsoTrack({
      output: null,
      slices: [slice],
      repeats: 2,
      sustain: 1,
      style: 1,
      voicing: 3,
    });
    sequencer.addTrack('1', track);
    sequencer.run();
  }, []);

  const buttonPress = (row: number, col: number) => {
    console.log('button press', row, col);
  };

  const keyAction = (key: string, release: boolean) => {
    if (key in keyMap) {
      console.log(keyMap[key]);
      const x = keyMap[key];
      if (x[0] === 'knob') {
        const knob = constants.knobs[x[1]][x[2]];
        console.log('knob', knob);
        if (control) {
          if (knob.alt_mode) {
            if (release) {
              console.log('releasemode');
              setModes(modes.slice(0, modes.length - 1));
            } else {
              console.log('setmode', knob.alt_mode);
              setModes([...modes, knob.alt_mode]);
            }
          }
        } else if (release) {
          console.log('releasemode');
          setModes(modes.slice(0, modes.length - 1));
        } else {
          console.log('setmode', knob.mode);
          setModes([...modes, knob.mode]);
        }
      }
    } else if (key === 'Control') {
      setControl(!release);
    }
  };

  const keyPress = (key: string) => {
    console.log('keyPress', key);
    keyAction(key, false);
  };

  const keyRelease = (key: string) => {
    console.log('keyRelease', key);
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
    console.log(settings, midiOutputs);
    setOutputs(settings.midiOutputs);
    sequencer.output = settings.midiOutputs.length ? midiOutputs[settings.midiOutputs[0]] : null;
  };

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
                  control={control}
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
                <Button b={b} row={0} col={i} onClick={buttonPress} state={ButtonState.inactive} />
              </td>
            ))}
          </tr>
          <tr>
            {constants.buttons[1].map((b, i) => (
              <td key={i}>
                <Button b={b} row={1} col={i} onClick={buttonPress} state={ButtonState.inactive} />
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
