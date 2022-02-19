import './MidiConfig.css';
import { useState } from 'react';
import { useGetAndSet, useStoreValue } from 'react-context-hook';
import { CallbackMap, MidiCallback } from '../types';

export function MidiConfig({ inputCallback }: { inputCallback: MidiCallback }) {
  const [open, setOpen] = useState(false);
  const midiInputs = useStoreValue('midiInputs');
  const midiOutputs = useStoreValue('midiInputs');
  const [midiCallbackMap, setMidiCallbackMap] = useGetAndSet<CallbackMap>('midiCallbackMap');

  const onToggle = (val: boolean) => {
    console.log('click');
    setOpen(val);
  };

  const toggleInput = () => {
    console.log('in togs');
  };

  const toggleOutput = () => {};

  return (
    <div className="midi-config">
      <img src="/icons/settings.svg" onClick={() => onToggle(!open)} className="midi-config-dropdown" />
      <div className="midi-config-dropdown-content" style={{ display: open ? 'block' : 'none' }}>
        <table cellPadding={6} cellSpacing={0} style={{ width: '100%' }}>
          <tbody>
            <tr>
              <th colSpan={3} className="midi-config-header">
                MIDI Inputs
              </th>
            </tr>
            <tr>
              <th>Device</th>
              <th>Manufacturer</th>
              <th>Connection</th>
            </tr>
            {Object.values(midiInputs).map((i: any) => {
              // if (inputCallback) {
              //   const tmp = midiCallbackMap[i.id] || {};
              //   const tmp2 = { ...tmp, [i.id]: inputCallback };
              //   setMidiCallbackMap({ ...midiCallbackMap, [i.id]: tmp2 });
              // }

              return (
                <tr key={i.id} onClick={() => toggleInput()} className="midi-config-select">
                  <td>{i.name}</td>
                  <td>{i.manufacturer}</td>
                  <td>{i.connection}</td>
                </tr>
              );
            })}

            <tr>
              <th colSpan={3} className="midi-config-header">
                MIDI Outputs
              </th>
            </tr>
            <tr>
              <th>Device</th>
              <th>Manufacturer</th>
              <th>Connection</th>
            </tr>
            {Object.values(midiOutputs).map((i: any) => {
              // midiCallbacks.listen(i.id, callback, callback);

              return (
                <tr key={i.id} onClick={() => toggleOutput()} className="midi-config-select">
                  <td>{i.name}</td>
                  <td>{i.manufacturer}</td>
                  <td>{i.connection}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
