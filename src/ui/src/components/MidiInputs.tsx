import { useContext } from 'react';
import { MidiContext } from '../contexts/MidiContext';

interface MidiInputsProps {
  callback: any;
}

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
export const MidiInputs = ({ callback }: MidiInputsProps) => {
  const { midiInputs } = useContext(MidiContext);

  console.log('midiinputs render', midiInputs);

  return (
    <table cellPadding={6} cellSpacing={0}>
      <tbody>
        <tr>
          <th colSpan={3}>MIDI Inputs</th>
        </tr>
        <tr>
          <th>Device</th>
          <th>Manufacturer</th>
          <th>Connection</th>
        </tr>
        {Object.values(midiInputs).map((i: any) => {
          // midiCallbacks.listen(i.id, callback, callback); // FIXME this used to come from the store?
          return (
            <tr key={i.id}>
              <td>{i.name}</td>
              <td>{i.manufacturer}</td>
              <td>{i.connection}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};
