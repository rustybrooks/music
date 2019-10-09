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
      <tr>
        <th>Command</th>
        <th>Channel</th>
        <th>Note</th>
        <th>Velocity</th>
      </tr>
      {
        messages.map((m, i) => {
          // console.log(m, i)
          return <tr key={i}>
            <td>{m.command}</td>
            <td>{m.channel}</td>
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
