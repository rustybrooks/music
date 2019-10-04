import React, { useState, useEffect } from 'react';

const MidiInputs = () => {
  const [midiInputs, set_midiInputs] = useState([]);

  useEffect(() => {
    navigator.requestMIDIAccess().then(function(access) {
      console.log("updating midi list")
      set_midiInputs(Array.from(access.inputs))
      console.log("inputs", midiInputs)
    })
  }, [])

  console.log('render', midiInputs)
  return (
    <table border={1} cellPadding={3} cellSpacing={0}><tbody>
      {
        midiInputs.map((kv) => {
          console.log(kv)
          return <tr key={kv[1].id}>
            <td>Device Name</td>
            <td>{kv[1].name}</td>
          </tr>
        })
      }
    </tbody></table>
  )
}

export default MidiInputs
