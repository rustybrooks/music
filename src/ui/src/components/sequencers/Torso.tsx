import * as constants from './TorsoConstants';

import './Torso.css';
import { MidiConfig, Settings } from '../MidiConfig';
import { CallbackMap, MidiCallback, MidiInputs, MidiMessage, MidiOutputs } from '../../types';
import { useGetAndSet } from 'react-context-hook';

function Knob({ k }: { k: any }) {
  return (
    <div style={{ textAlign: 'center', padding: '.4rem' }}>
      <svg width="4rem" height="4rem" viewBox="0 0 20 20" version="1.1" transform="rotate(45)">
        <circle fill="#aa6666" fillRule="evenodd" stroke="#a10000" strokeWidth=".5" strokeOpacity="1" cx="10" cy="10" r="9" />
        <circle fill="#000000" cx="10" cy="4" r="2" />
      </svg>{' '}
      <div style={{ fontSize: '.8rem' }}>{k.label}</div>
      <div style={{ fontSize: '.8rem' }}>{k.alt_label}&nbsp;</div>
    </div>
  );
}

function Button({ b }: { b: any }) {
  if (b === null) {
    return <div style={{ width: '4rem', height: '4rem' }} />;
  }
  return (
    <div style={{ textAlign: 'center', verticalAlign: 'top', fontSize: '1rem' }}>
      <div style={{ display: 'flex', textAlign: 'left' }}>
        <div style={{ width: '3rem', height: '3rem', backgroundColor: '#999' }} />
        <div
          style={{
            transform: 'rotate(-90deg) translate(0, 1.1rem)',
            position: 'relative',
            float: 'right',
            height: '3rem',
            width: '.8rem',
            textAlign: 'left',
            verticalAlign: 'top',
            padding: 'auto',
            fontSize: '.6rem',
          }}
        >
          {b[1]}&nbsp;
        </div>
      </div>
      <div style={{ fontSize: '.8rem' }}>{b[0]}&nbsp;</div>
    </div>
  );
}

export function Torso() {
  const [midiCallbackMap, setMidiCallbackMap] = useGetAndSet<CallbackMap>('midiCallbackMap');
  const [midiInputs, setMidiInputs] = useGetAndSet<MidiInputs>('midiInputs');
  const [midiOutputs, setMidiOutputs] = useGetAndSet<MidiOutputs>('midiOutputs');
  const [midiAccess, setMidiAccess] = useGetAndSet<WebMidi.MIDIAccess>('midiAccess');
  // const midiCallback: MidiCallback = (message: MidiMessage): void => {
  //   console.log(message);
  // };

  function sendMiddleC() {
    const noteOnMessage = [0x90, 60, 0x7f]; // note on middle C, full velocity
    const output = midiAccess.outputs.get(Object.keys(midiOutputs)[0]);
    output.send(noteOnMessage); // omitting the timestamp means send immediately.
    output.send([0x80, 60, 0x40], window.performance.now() + 1000.0); // timestamp = now + 1000ms.
  }

  const settingsCallback = (settings: Settings) => {
    console.log(settings);
    sendMiddleC();
  };

  return (
    <div style={{ display: 'inline-block', background: '#ddd', position: 'relative' }}>
      <MidiConfig settingsCallback={settingsCallback} />
      <table style={{ width: '100%' }}>
        <tbody>
          <tr>
            {constants.knobs[0].map((k, i) => (
              <td key={i}>
                <Knob k={k} />
              </td>
            ))}
          </tr>
          <tr>
            {constants.knobs[1].map((k, i) => (
              <td key={i}>
                <Knob k={k} />
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
                <Button b={b} />
              </td>
            ))}
          </tr>
          <tr>
            {constants.buttons[1].map((b, i) => (
              <td key={i}>
                <Button b={b} />
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
