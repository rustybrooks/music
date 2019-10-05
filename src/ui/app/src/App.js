import React, { useState, useEffect } from 'react';

import { createStore, store } from '@spyna/react-store'
import Piano from './components/instruments/Piano'

const MidiCallbacks = () => {

  function init() {
    let callbackMap = {}

    console.log("initializing midi")
    navigator.requestMIDIAccess().then(function (access) {
      for (let input of access.inputs.values()) {
        console.log('midi input', input)
        input.onmidimessage = callback;
        callbackMap[input.id] = input
      }

      store.set('midiInputs', callbackMap)
      access.onstatechange = (e) => {
        let midiInputs = store.get('midiInputs')
        store.set('midiInputs', {...midiInputs, [e.port.id]: e.port})
      }
    })
  }

  function add() {}
  function callback(m) {
    console.log(m)
  }

    return Object.freeze({
      init,
    });
}

let midiCallbacks = MidiCallbacks()

const App = (props) => {
  useEffect(() => {
    midiCallbacks.init()
  }, [])
  return (
      <div>
        <Piano/>
      </div>
    )
}

const initialValue = {
  'midiCallbacks': MidiCallbacks(),
  'midiInputs': {},
}

const config = {}

export default createStore(App, initialValue, config)


