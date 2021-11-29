import * as React from "react";
import * as ReactDOM from "react-dom";
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { withStore, useGetAndSet } from 'react-context-hook'

// import { Link } from 'react-router-dom'
import { withStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
// import { withRouter } from 'react-router'

import MidiMessage from "./lib/MidiMessage";

interface MidiCallback {
  (message: MidiMessage): null
}

interface MidiInputs {
  [id: number]: any
}

interface CallbackMap {
  [id: number]: {[id: number]: MidiCallback}
}


const styles = {
  root: {
    flexGrow: 1,
  },
  flex: {
    flexGrow: 1,
  },

  tabLink : {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    'padding-right': 0,
    'padding-left': 0,
  }

};

const NavBarX = ({classes} : any) => {
  let midiInputs : MidiInputs;
  let setMidiInputs : any;
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

  [midiInputs, setMidiInputs] = useGetAndSet('midiInputs')

  React.useEffect(() => {
    init()
  }, [])


    return (
        <div className={classes.root}>
            <AppBar position="static">
                <Tabs value={0}>
                    <Tab
                        key='Home'
                        label='home'
                        className={classes.tabLink}
                    />
                </Tabs>
            </AppBar>
        </div>
    )
}

const initialValue = {
  'midiCallbackMap': {},
  'midiInputs': {},
}

const NavBar = withStore(withStyles(styles)(NavBarX), initialValue)


ReactDOM.render(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<NavBar/>} />
      </Routes>
    </BrowserRouter>,
    document.getElementById("root")
);

