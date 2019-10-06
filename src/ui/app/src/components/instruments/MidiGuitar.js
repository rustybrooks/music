import React, { useState, useEffect } from 'react';
import { withStyles, makeStyles } from '@material-ui/core/styles'

import MidiMonitor from "../MidiMonitor"
import MidiInputs from "../MidiInputs"
import Guitar from './Guitar/index.js'
const style = theme => ({
})

const MidiGuitar = ({classes}) => {
  const init_grid = () => {
    let igrid = []
    for (let y=0; y<9; y++) {
      let row = []
      for (let y=0; y<9; y++) {
        row.push({class: 'blank'})
      }
      igrid.push(row)
    }
    return igrid
  }

  const our_callback = (m) => {
//    const [x, y] = note_to_grid(m.note)
  }


  return <div>
    <Guitar handed='left'/>
    <MidiMonitor/>
    <MidiInputs callback={our_callback}/>
  </div>
}

export default withStyles(style)(MidiGuitar)





