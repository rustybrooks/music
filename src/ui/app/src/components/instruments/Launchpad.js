import React, { useState, useEffect } from 'react';
import { withStyles, makeStyles } from '@material-ui/core/styles'

import MidiMonitor from "../MidiMonitor"
import MidiInputs from "../MidiInputs"


const style = theme => ({
  'blank': {
    background: '#ddd',
    padding: 4,
  },

  'press': {
    background: 'blue'
  }
})

const Launchpad = ({classes}) => {
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
    const [x, y] = note_to_grid(m.note)

    let c = null
    if (m.command === 'NoteOn') {
      c = 'press'
    } else if (m.command === 'NoteOff') {
      c = 'blank'
    }
    setGrid(g => {
      g[y][x]['class'] = c
      return g.slice(0)
    })
  }

  const note_to_grid = (note) => {
    console.log(note)
    const row = 1 + Math.trunc(note / 16)
    const col = note % 16
    return [col, row]
  }

  let [grid, setGrid] = useState(init_grid())

  return <div>
    <table>
      <tbody>
      {
        [0, 1, 2, 3, 4, 5, 6, 7, 8].map((y) => {
          return <tr key={y}>
            {
              [0, 1, 2, 3, 4, 5, 6, 7, 8].map((x) => {
                if (y === 0 && x === 8) {
                  return <td key={x}>&nbsp;</td>
                } else {
                  const c = classes[grid[y][x]['class']]
                  return <td key={x}><div className={c}>{y} - {x}</div></td>

                }
              })
            }
          </tr>
        })
      }
      </tbody>
    </table>
    <MidiMonitor/>
    <MidiInputs callback={our_callback}/>
  </div>
}

export default withStyles(style)(Launchpad)