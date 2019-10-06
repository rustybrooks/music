import React, { useState, useEffect } from 'react';
import MidiInputs from "./MidiInputs"

const MidiMonitor = () => {
  const [messages, setMessages] = useState([])

  const our_callback = (m) => {
    messages.push(m)
    setMessages(messages.slice(-10))
  }

  return <div>
    <table>
      <tbody>
      {
        messages.map((m, i) => {
          // console.log(m, i)
          return <tr key={i}>
            <td>{m.command}</td>
            <td>{m.note}</td>
            <td>{m.velocity}</td>
          </tr>
        })
      }
      </tbody>
    </table>
    <MidiInputs callback={our_callback}/>
  </div>
}

export default MidiMonitor