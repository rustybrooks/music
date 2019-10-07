import React, { useState, useEffect } from 'react';
import { withStyles, makeStyles } from '@material-ui/core/styles'

import MidiMonitor from "../MidiMonitor"
import MidiInputs from "../MidiInputs"
import Guitar from './Guitar/index.js'
const style = theme => ({
})

const MidiGuitar = ({classes}) => {
  const our_callback = (m) => {
    if (m.note >= 0 && m.note <= 8) {
      const c = (m.command === 'NoteOn') ? 'press' : 'blank'
      setFretboard(f => {
        f[0][m.note] = {'class': c}
        return f.slice(0)
      })
    }
  }

  let [fretboard, setFretboard] = useState(init_fretboard())

  function init_fretboard() {
    const frets = 25
    return [...Array(6)].map(() => {
      return [...Array(frets+1)].map((v) => {return {'class': 'blank'}})
    })
  }


  return <div>
    <Guitar handed='left' fretboard={fretboard}/>
    <MidiMonitor/>
    <MidiInputs callback={our_callback}/>
  </div>
}

export default withStyles(style)(MidiGuitar)





