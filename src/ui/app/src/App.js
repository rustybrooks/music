import React, { useState, useEffect } from 'react';

import { createStore } from '@spyna/react-store'
import Piano from './components/instruments/Piano'

const MidiCallbacks = () => {
  let callbackMap = {}

  function init() {
    console.log("initializing midi")
    navigator.requestMIDIAccess().then(function (access) {
      console.log("updating midi list")
      for (let input of access.inputs.values()) {
        input.onmidimessage = callback;
      }

      access.onstatechange = (e) => {
        console.log("MIDI State change event", e)
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

const App = () => {
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
  'midi-callbacks': MidiCallbacks(),
}

const config = {}

export default createStore(App, initialValue, config)


