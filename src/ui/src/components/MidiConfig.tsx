import './MidiConfig.css';
import { useState } from 'react';

export function MidiConfig() {
  const [open, setOpen] = useState(false);

  const onClick = (val: boolean) => {
    console.log('click');
    setOpen(val);
  };

  return (
    <div className="midi-config" onClick={() => onClick(!open)}>
      <img src="/icons/settings.svg" onClick={() => onClick(!open)} />
      <div className="midi-config-dropdown"></div>
      <div className="midi-config-dropdown-content" style={{ display: open ? 'block' : 'none' }}>
        Stuff here
      </div>
    </div>
  );
}
