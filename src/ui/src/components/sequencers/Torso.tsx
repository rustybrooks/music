import { useCallback, useEffect } from 'react';
import { useGetAndSet } from 'react-context-hook';

import * as constants from './TorsoConstants';

import './Torso.css';

function Knob({ k }: { k: any }) {
  return (
    <div style={{ textAlign: 'center', padding: '.5rem' }}>
      <img src="/widgets/Knob.svg" alt="knob" style={{ transform: 'rotate(90deg)' }} />
      <div>{k.label}</div>
      <div>{k.alt_label}&nbsp;</div>
    </div>
  );
}

function Button({ b }: { b: any }) {
  if (b === null) {
    return <div style={{ width: '5rem', height: '5rem' }} />;
  }
  return (
    <div style={{ textAlign: 'center', verticalAlign: 'top' }}>
      <div style={{ width: '5rem', height: '5rem', backgroundColor: '#66a' }} />
      <div>{b[0]}&nbsp;</div>
    </div>
  );
}

export function Torso() {
  return (
    <div style={{ display: 'inline-block' }}>
      <table style={{ width: '100%' }}>
        <tbody>
          <tr>
            {constants.knobs[0].map((k, i) => (
              <td key={i}>
                <Knob k={k} />
              </td>
            ))}
          </tr>
          <tr>
            {constants.knobs[1].map((k, i) => (
              <td key={i}>
                <Knob k={k} />
              </td>
            ))}
          </tr>
        </tbody>
      </table>

      <table style={{ width: '100%' }}>
        <tbody>
          <tr>
            {constants.buttons[0].map((b, i) => (
              <td key={i}>
                <Button b={b} />
              </td>
            ))}
          </tr>
          <tr>
            {constants.buttons[1].map((b, i) => (
              <td key={i}>
                <Button b={b} />
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
