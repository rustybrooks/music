import React from 'react';
import { withStore } from '@spyna/react-store'

const MidiInputs = ({midiInputs, midiCallbacks, callback}) => {
  // console.log('midiinputs render', midiInputs)

  return (
    <table border={1} cellPadding={6} cellSpacing={0}>
      <tbody>
      <tr><th colSpan={3}>MIDI Inputs</th></tr>
      <tr><th>Device</th><th>Manufacturer</th><th>Connection</th></tr>
      {
        Object.values(midiInputs).map((i) => {
          midiCallbacks.listen(i.id, callback, callback)
          return <tr key={i.id}>
            <td>{i.name}</td>
            <td>{i.manufacturer}</td>
            <td>{i.connection}</td>
          </tr>
        })
      }
      </tbody>
    </table>
  )
}

export default withStore(MidiInputs, ['midiInputs', 'midiCallbacks'])
