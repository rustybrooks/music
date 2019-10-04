import React, { useState, useEffect } from 'react';

function connectToDevice(device) {
  console.log('Connecting to device', device);
  device.onmidimessage = function(m) {
    const [command, key, velocity] = m.data;
    if (command === 145) {
      debugEl.innerText = 'KEY UP: ' + key;
    } else if(command === 129) {
      debugEl.innerText = 'KEY DOWN';
    }
  }
}

const MidiInputs = () => {
  const [midiInputs, set_midiInputs] = useState([]);

  useEffect(() => {
    navigator.requestMIDIAccess().then(function(access) {
      console.log("updating midi list")
      set_midiInputs(Array.from(access.inputs))
      console.log("inputs", midiInputs)
    })

    access.onstatechange = (e) => {
      console.log("MIDI State change event", e)
    }
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
