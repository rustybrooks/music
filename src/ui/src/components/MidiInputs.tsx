import * as React from 'react';
import { withStore, useStoreValue } from 'react-context-hook'

interface MidiInputsProps {
    callback : any;
}

const MidiInputs = ({callback} : MidiInputsProps) => {
    const midiInputs = useStoreValue('midiInputs')
    const midiCallbacks = useStoreValue('midiCallbacks')
    console.log('midiinputs render', midiInputs)

  return (
    <table cellPadding={6} cellSpacing={0}>
      <tbody>
      <tr><th colSpan={3}>MIDI Inputs</th></tr>
      <tr><th>Device</th><th>Manufacturer</th><th>Connection</th></tr>
      {
        Object.values(midiInputs).map((i : any) => {
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

export default MidiInputs
