import { useCallback, useEffect } from 'react';
import { useGetAndSet } from 'react-context-hook';

import * as constants from './TorsoConstants';

import './Torso.css';

function Knob({ k }: { k: any }) {
  return (
    <div style={{ textAlign: 'center', padding: '.5rem' }}>
      <svg width="20mm" height="20mm" viewBox="0 0 20 20" version="1.1" transform="rotate(45)">
        <circle fill="#ff0000" fillRule="evenodd" stroke="#a10000" strokeWidth=".5" strokeOpacity="1" cx="10" cy="10" r="9" />
        <circle fill="#000000" cx="10" cy="4" r="2" />
      </svg>{' '}
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
