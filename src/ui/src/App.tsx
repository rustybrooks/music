import * as React from 'react'
import { hot } from "react-hot-loader"

import { withStore, useStore } from 'react-context-hook'

import MidiMessage from "./MidiMessage"
import Launchpad from "./components/instruments/Launchpad"
// import MidiGuitar from "./components/instruments/MidiGuitar"


interface MidiCallback {
  (message: MidiMessage): null
}

interface MidiInputs {
  [id: number]: any
}

interface CallbackMap {
  [id: number]: {[id: number]: MidiCallback}
}

const Home = () => {
  return (
      <div>
        Home
      </div>
  )
}


const App = () => {
  let midiInputs : MidiInputs;
  let setMidiInputs : any;
  let deleteMidiInputs : any

  let callbackMap : CallbackMap = {}

  let access_callback = (access : any) => {
    let _midiInputs : MidiInputs = {}

    for (let input of access.inputs.values()) {
      input.onmidimessage = callback;
      callbackMap[input.id] = {}
      midiInputs[input.id] = input
    }

    access.onstatechange = (e : any) => {
      setMidiInputs({...midiInputs, [e.port.id]: e.port})
    }

    setMidiInputs(_midiInputs);
  }

  let init = () => {
    console.log("init pre")
    navigator.requestMIDIAccess().then(access_callback)
    console.log("init post")
  }

  let listen = (midi_id : number, listen_id : number, callback : MidiCallback) => {
    // console.log('listen', midi_id, callback)
    callbackMap[midi_id][listen_id] = callback
  }

  let callback = (m : any) => {
    const message = new MidiMessage(m)
    // console.log(m)
    const midi_id = m.target.id
    // console.log("midi cb", midi_id, callbackMap[midi_id])
    Object.values(callbackMap[midi_id]).forEach((cb) => {
       cb(message)
    })
  }

  [midiInputs, setMidiInputs, deleteMidiInputs] = useStore('midiInputs')

  React.useEffect(() => {
    init()
  }, [])


  return <div>
    App
  </div>

}

const initialValue = {
  'midiCallbackMap': {},
  'midiInputs': {},
}

export default withStore(App, initialValue)


