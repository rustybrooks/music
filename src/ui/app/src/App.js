import React, { useState, useEffect } from 'react';

import { createStore, store } from '@spyna/react-store'
import Launchpad from "./components/instruments/Launchpad"
import MidiMessage from "./MidiMessage"


const MidiCallbacks = () => {
  let callbackMap = {}

  let access_callback = (access) => {
    let midiInputs = {}
    for (let input of access.inputs.values()) {
      input.onmidimessage = callback;
      callbackMap[input.id] = {}
      midiInputs[input.id] = input
    }

    access.onstatechange = (e) => {
      let midiInputs = store.get('midiInputs')
      store.set('midiInputs', {...midiInputs, [e.port.id]: e.port})
    }

    store.set('midiInputs', midiInputs)
  }

  let init = () => {
    navigator.requestMIDIAccess().then(access_callback)
  }

  let listen = (midi_id, listen_id, callback) => {
    // console.log('listen', midi_id, listen_id, callback)
    callbackMap[midi_id][listen_id] = callback
  }

  let callback = (m) => {
    const message = MidiMessage(m)
    // console.log(m)
    const midi_id = m.target.id
    // console.log("midi cb", midi_id, callbackMap[midi_id])
    Object.values(callbackMap[midi_id]).forEach((cb) => {
       cb(message)
    })
  }

  return Object.freeze({
    init, listen, callbackMap
  });
}

let midiCallbacks = MidiCallbacks()

const App = (props) => {
  useEffect(() => {
    midiCallbacks.init()
  }, [])
  return (
      <div>
        <Launchpad/>
      </div>
    )
}

const initialValue = {
  'midiCallbacks': midiCallbacks,
  'midiInputs': {},
}

const config = {}

export default createStore(App, initialValue, config)


