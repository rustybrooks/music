import * as React from 'react';
import { withStyles, makeStyles } from '@material-ui/core/styles'

import MidiMonitor from "../MidiMonitor"
import MidiInputs from "../MidiInputs"
import { Note, NoteType } from '../../Note'
import MidiMessage from "../../MidiMessage"

// import * as exercises from '../../exercises/launchpad'

// function sendMiddleC( midiAccess, portID ) {
//   var noteOnMessage = [0x90, 60, 0x7f];    // note on, middle C, full velocity
//   var output = midiAccess.outputs.get(portID);
//   output.send( noteOnMessage );  //omitting the timestamp means send immediately.
//   output.send( [0x80, 60, 0x40], window.performance.now() + 1000.0 ); // Inlined array creation- note off, middle C,
//                                                                       // release velocity = 64, timestamp = now + 1000ms.
// }


const style = () => {
  let x : any = {
    outterButton: {
      padding: 10,
      'align-items': 'center',
    },

    button: {
      padding: 5,
    }
  }
  x.pressBlank = {...x.button, ['background-color']: '#eee'}
  x.press = {...x.button, ['background-color']: '#66F'}
  x.pressError = {...x.button, ['background-color']: '#F66'}

  x.selectBlank = {...x.outterButton, ['background-color']: '#eee'}
  x.select = {...x.outterButton, ['background-color']: '#3A9'}

  return x
}

interface LaunchpadProps {
  classes : any
}

const Launchpad = ({classes} : LaunchpadProps) => {
  // const exercise = exercises.FindNotes([], [Note(["A", 0])])

  const init_grid = () => {
    let igrid = []
    for (let y=0; y<9; y++) {
      let row = []
      for (let y=0; y<9; y++) {
        row.push({pressed: false, error: false, selected: false})
      }
      igrid.push(row)
    }
    return igrid
  }

  const midi_callback = (m : MidiMessage) => {
    // const [x, y] = note_to_grid(m.note)
    // const grid_events = exercise.callback(x, y, m.note, m.command === m.NOTEON)

    // let ng = grid.splice(0)
    //
    // grid_events.forEach((e) => {
    //   if (e[0] === 'set_press') {
    //     ng[y][x].pressed = ['press', 'error'].includes(e[1])
    //     ng[y][x].error = e[1] === 'error'
    //     console.log("pressed", ng[y][x].pressed, 'error', ng[y][x].error)
    //   } else {
    //     console.log("what", e)
    //   }
    // })
    //
    // setGrid(ng)
  }

  // const note_to_grid = (note : Note) => {
  //   console.log(note)
  //   const row = 1 + Math.trunc(note.number / 16)
  //   const col = note.number % 16
  //   return [col, row]
  // }

  let [grid, setGrid] = React.useState(() => init_grid())

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
                  const g = grid[y][x]
                  const c1 = g.selected ? 'select' : 'selectBlank'
                  const c2 = g.pressed ? (g.error ? 'pressError' : 'press') : 'pressBlank'
                  return <td key={x} className={classes[c1]}>
                    <div className={classes[c2]}>
                      {y}, {x}
                    </div>
                  </td>

                }
              })
            }
          </tr>
        })
      }
      </tbody>
    </table>
    <MidiMonitor/>
    <MidiInputs callback={midi_callback}/>
  </div>
}

export default withStyles(style)(Launchpad)
