import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { withStore, useGetAndSet } from 'react-context-hook';

import { render } from 'react-dom';
import { useCallback, useEffect } from 'react';
import { AppBar } from './components/AppBar';
import { Home } from './components/instruments/Home';

import './index.css';
import { Torso } from './components/sequencers/Torso';
import { CallbackMap, MidiInputs, MidiMessage, MidiOutputs } from './types';

const initialValue = {
  midiCallbackMap: {},
  midiInputs: {},
  midiOutputs: {},
};

function AppX() {
  const [midiInputs, setMidiInputs] = useGetAndSet<MidiInputs>('midiInputs');
  const [midiOutputs, setMidiOutputs] = useGetAndSet<MidiOutputs>('midiOutputs');
  const [callbackMap] = useGetAndSet<CallbackMap>('midiCallbackMap');

  const callback = (m: any) => {
    const message = new MidiMessage(m);
    console.log(m);
    const midi_id = m.target.id;
    console.log('midi cb', midi_id, callbackMap[midi_id]);
    Object.values(callbackMap[midi_id]).forEach(cb => {
      cb(message);
    });
  };

  console.log('ins', midiInputs);

  const onChangeCallback = useCallback(
    (e: any) => {
      // console.log('onstatechange', e);
      console.log(e.port.id, e.port.name, e.port.state, e.port.type, e.port.connection);
      if (e.port.type === 'input') {
        if (e.port.state === 'connected') {
          setMidiInputs({ ...midiInputs, [e.port.id]: e.port });
        } else {
          setMidiInputs(Object.fromEntries(Object.entries(midiInputs).filter(entry => entry[0] !== e.port.id)));
        }
      } else if (e.port.state === 'connected') {
        setMidiOutputs({ ...midiOutputs, [e.port.id]: e.port });
      } else {
        setMidiOutputs(Object.fromEntries(Object.entries(midiOutputs).filter(entry => entry[0] !== e.port.id)));
      }
    },
    [midiInputs, midiOutputs],
  );

  const accessCallback = (access: any) => {
    const thesemidiInputs: MidiInputs = {};
    const thesemidiOutputs: MidiOutputs = {};

    for (const input of access.inputs.values()) {
      input.onmidimessage = callback;
      callbackMap[input.id] = {};
      thesemidiInputs[input.id] = input;
    }

    for (const output of access.outputs.values()) {
      output.onmidimessage = callback;
      callbackMap[output.id] = {};
      thesemidiOutputs[output.id] = output;
    }

    setMidiInputs(thesemidiInputs);
    setMidiOutputs(thesemidiOutputs);
    access.onstatechange = onChangeCallback;
  };

  const init = () => {
    console.log('init pre');
    navigator.requestMIDIAccess().then(accessCallback);
    console.log('init post');
  };

  // const listen = (midi_id: number, listen_id: number, cb: MidiCallback) => {
  //   // console.log('listen', midi_id, callback)
  //   callbackMap[midi_id][listen_id] = cb;
  // };

  useEffect(() => {
    init();
  }, []);

  return (
    <BrowserRouter>
      <AppBar />
      <div style={{ width: '100%', padding: '1rem' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/torso" element={<Torso />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

const App = withStore(AppX, initialValue);

render(<App />, document.getElementById('root'));
