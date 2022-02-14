import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { withStore, useGetAndSet } from 'react-context-hook';

import { render } from 'react-dom';
import { useEffect } from 'react';
import MidiMessage from './lib/MidiMessage';
import { AppBar } from './components/AppBar';
import { Home } from './components/instruments/Home';

import './index.css';
import { Torso } from './components/sequencers/Torso';

interface MidiCallback {
  (message: MidiMessage): null;
}

interface MidiInputs {
  [id: number]: any;
}

interface CallbackMap {
  [id: number]: { [id: number]: MidiCallback };
}

const initialValue = {
  midiCallbackMap: {},
  midiInputs: {},
};

function AppX() {
  const [midiInputs, setMidiInputs] = useGetAndSet<MidiInputs>('midiInputs');
  const [callbackMap, setCallbackMap] = useGetAndSet<CallbackMap>('midiCallbackMap');

  const callback = (m: any) => {
    const message = new MidiMessage(m);
    // console.log(m)
    const midi_id = m.target.id;
    // console.log("midi cb", midi_id, callbackMap[midi_id])
    Object.values(callbackMap[midi_id]).forEach(cb => {
      cb(message);
    });
  };

  const access_callback = (access: any) => {
    const thesemidiInputs: MidiInputs = {};

    for (const input of access.inputs.values()) {
      input.onmidimessage = callback;
      callbackMap[input.id] = {};
      thesemidiInputs[input.id] = input;
    }

    access.onstatechange = (e: any) => {
      setMidiInputs({ ...thesemidiInputs, [e.port.id]: e.port });
    };

    setMidiInputs(thesemidiInputs);
  };

  const init = () => {
    console.log('init pre');
    navigator.requestMIDIAccess().then(access_callback);
    console.log('init post');
  };

  const listen = (midi_id: number, listen_id: number, cb: MidiCallback) => {
    // console.log('listen', midi_id, callback)
    callbackMap[midi_id][listen_id] = cb;
  };

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
