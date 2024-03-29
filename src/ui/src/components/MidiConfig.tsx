import './MidiConfig.css';
import { useState } from 'react';
import { useStoreValue } from 'react-context-hook';

export interface Settings {
  midiInputs: number[];
  midiOutputs: number[];
}

type SettingsCallback = {
  (settings: Settings): void;
};

export function MidiConfig({ settingsCallback }: { settingsCallback: SettingsCallback }) {
  const [open, setOpen] = useState(false);
  const [selectedIns, setSelectedIns] = useState([]);
  const [selectedOuts, setSelectedOuts] = useState([]);
  const midiInputs = useStoreValue('midiInputs');
  const midiOutputs = useStoreValue('midiOutputs');

  const onToggle = (val: boolean) => {
    setOpen(val);
  };

  const toggleInput = (port_id: number) => {
    console.log('toggle', port_id);
    if (selectedIns.includes(port_id)) {
      setSelectedIns(selectedIns.filter(i => i.id !== port_id));
    } else {
      setSelectedIns([...selectedIns, port_id]);
    }
    settingsCallback({
      midiInputs: selectedIns,
      midiOutputs: selectedOuts,
    });
  };

  const toggleOutput = (port_id: number) => {
    if (selectedOuts.includes(port_id)) {
      setSelectedOuts(selectedOuts.filter(i => i.id !== port_id));
    } else {
      setSelectedOuts([...selectedOuts, port_id]);
    }
    settingsCallback({
      midiInputs: selectedIns,
      midiOutputs: selectedOuts,
    });
  };

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
              // console.log('in', i);

              return (
                <tr key={i.id} onClick={() => toggleInput(i.id)} className="midi-config-select">
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
              // console.log('out', i);

              return (
                <tr key={i.id} onClick={() => toggleOutput(i.id)} className="midi-config-select">
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
