import React from 'react';
import { withStore } from '@spyna/react-store'

const MidiInputs = ({midiInputs, midiCallbacks}) => {
  console.log('midiinputs', midiInputs)

  const our_callback = (m) => {
    console.log("our_callback", m)
  }

  return (
    <table border={1} cellPadding={6} cellSpacing={0}>
      <tbody>
      <tr><th colSpan={3}>MIDI Inputs</th></tr>
      <tr><th>Device</th><th>Manufacturer</th><th>Connection</th></tr>
      {
        Object.values(midiInputs).map((i) => {
          midiCallbacks.listen(i.id, 'foo', our_callback)
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
