import * as React from 'react';
import { MidiInputs } from './MidiInputs';
import { MidiMessage } from '../types';

export const MidiMonitor = () => {
  const [messages, setMessages] = React.useState<MidiMessage[]>([]);

  const our_callback = (m: any) => {
    messages.push(m);
    setMessages(messages.slice(-20));
  };

  return (
    <div>
      <table>
        <tbody>
          <tr>
            <th>Command</th>
            <th>Channel</th>
            <th>Note</th>
            <th>Velocity</th>
          </tr>
          {messages.map((m, i) => {
            // console.log(m, i)
            return (
              <tr key={i}>
                <td>{m.command}</td>
                <td>{m.channel}</td>
                <td>{m.note}</td>
                <td>{m.velocity}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <MidiInputs callback={our_callback} />
    </div>
  );
};
