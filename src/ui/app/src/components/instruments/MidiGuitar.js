import React, { useState, useEffect } from 'react';
import { withStyles, makeStyles } from '@material-ui/core/styles'

import MidiMonitor from "../MidiMonitor"
import MidiInputs from "../MidiInputs"
import Note from '../../Note'


const tunings = {
  guitar: [['E', 0], ['A', 0], ['D', 1], ['G', 1], ['B', 1], ['E', 2]]
}

const magic = 0.9438743126816935


const style = theme => {
  let x = {
    'fretboard': {
      'display': 'flex',
      'width': '100%',
      'height': '200px'
    },
    'nut': {
      'display': 'flex',
      'width': '100%',
      'height': '100%',
      'flex-flow': 'column',
    },
    'fretboard2': {
      'display': 'flex',
      'width': '100%',
      'height': '100%'
    },
    'position': {
      'display': 'flex',
      'flex-flow': 'column',
      'height': '100%',
    },
    'marker': {
      'display': 'flex',
      'flex-flow': 'column',
      'height': '100%',
      '-webkit-box-pack': 'center',
      'justify-content': 'center',
      '-webkit-box-align': 'center',
      'align-items': 'center',
    },
    'fret': {
      display: 'flex',
      '-webkit-box-pack': 'center',
      'justify-content': 'center',
      '-webkit-box-align': 'center',
      'align-items': 'center',
      width: '100%',
      height: '100%',
    },
    'fret2': {
      'display': 'flex',
      '-webkit-box-pack': 'center',
      'justify-content': 'center',
      '-webkit-box-align': 'center',
      'align-items': 'center',
      'height': '80%',
      'width': '94%',
      'margin': '10% 3%',
      'border-width': '1px',
      'border-style': 'solid',
      'border-color': 'darkgrey',
      'border-image': 'initial',
      'border-radius': '3px',
    },
  }
  x['blank'] = {...x.fret2, ['background-color']: '#eee'}
  x['press'] = {...x.fret2, ['background-color']: 'blue'}

  return x
}

const MidiGuitar = ({classes, tuning, frets, handed}) => {
  tuning = (tuning === undefined) ? 'guitar' : tuning
  frets = (frets === undefined) ? 17 : frets
  handed = (handed === undefined) ? 'right' : handed
  const notes = (tuning in tunings ? tunings[tuning] : tuning).map(n => Note(n)).reverse()

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

  function fret(f) {
    let width = 100
    if (f) {
      // width = 5
      width = 12*(Math.pow(magic, f))
    }
    return <div style={{'width': width + '%'}} className={classes.position} key={f}>
      {
        notes.map((n, i) => {
          const fs = fretboard[i][f]

          return <div key={n.number} className={classes.fret}>
            <div className={classes[fs.class]}>
              {n.add(f).note}
            </div>
          </div>
        })
      }
      <div className={classes.marker}>
        {f}
      </div>
    </div>
  }

  function first(left=false) {
    let w = 10
    let x = left ? 100-w : 0
    return <svg key='first' width={w+"%"} height="100%" x={x+"%"} y="0">
      <foreignObject width="100%" height="100%">
        <div className={classes.nut}>
          {fret(0)}
        </div>
      </foreignObject>
    </svg>
  }

  function rest(left=false) {
    let w = 89.25
    let x = left ? 100-10.75-w : 10.75
    return <svg key='rest' width={w + "%"} height="100%" x={x+'%'} y="0">
      <g></g>
      <foreignObject width="100%" height="100%">
        <div className={classes.fretboard2}>
          {[...Array(frets).keys()].map(f => fret(left ? frets-f : f+1))}
        </div>
      </foreignObject>
    </svg>
  }

  function nut(left=false) {
    let w = 0.75
    let x = left ? 100 - 10 - w : 10
    return <svg key='nut' width={w+"%"} height="100%" x={x+"%"} y="0">
      <rect x="5%" y="2%" rx="3" ry="3" width="90%" height="96%" fill="lightgray" stroke="none"/>
    </svg>
  }

  function stuff() {
    // return [rest(handed==='left'), nut(handed==='left'), first(handed==='left')]
    return [first(handed==='left'), nut(handed==='left'), rest(handed==='left')]
  }

  return <div>
    <div className={classes.fretboard}>
      <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="100%" height="100%" stroke="black" strokeWidth="1"
           fill="white" shapeRendering="geometricPrecision" style={{overflow: "visible"}}>
        {stuff()}
      </svg>
    </div>
    <MidiMonitor/>
    <MidiInputs callback={our_callback}/>
  </div>
}

export default withStyles(style)(MidiGuitar)





