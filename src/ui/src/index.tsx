import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { withStore, useGetAndSet } from 'react-context-hook';

import { render } from 'react-dom';
import { useEffect } from 'react';
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
  const [, setMidiInputs] = useGetAndSet<MidiInputs>('midiInputs');
  const [, setMidiOutputs] = useGetAndSet<MidiOutputs>('midiOutputs');
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

  const access_callback = (access: any) => {
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

    access.onstatechange = (e: any) => {
      console.log('onstatechange', e);
      setMidiInputs({ ...thesemidiInputs, [e.port.id]: e.port });
      setMidiOutputs({ ...thesemidiOutputs, [e.port.id]: e.port });
    };

    setMidiInputs(thesemidiInputs);
  };

  const init = () => {
    console.log('init pre');
    navigator.requestMIDIAccess().then(access_callback);
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
