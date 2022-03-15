import { MouseEvent, useState } from 'react';

function pauseEvent<T>(e: MouseEvent<T>) {
  if (e.stopPropagation) e.stopPropagation();
  if (e.preventDefault) e.preventDefault();
  return false;
}

export function Knob({
  k,
  pressed,
  control,
  pressCallback,
  releaseCallback,
}: {
  k: any;
  pressed: boolean;
  control: boolean;
  pressCallback: any;
  releaseCallback: any;
}) {
  const colors = {
    normal: '#aa6666',
    pressed: '#aaaa66',
    control: '#aa66aa',
  };

  const [mousePressed, setMousePressed] = useState(false);
  const [origin, setOrigin] = useState(null);
  const [percent, setPercent] = useState(0);

  const onMouseDown = (event: MouseEvent<HTMLDivElement>) => {
    setMousePressed(true);
    setOrigin([event.clientX, event.clientY]);
    pauseEvent(event);
    pressCallback();
  };

  const onMouseUp = (event: MouseEvent<HTMLDivElement>) => {
    setMousePressed(false);
    releaseCallback();
  };

  const onMouseMove = (event: MouseEvent<HTMLDivElement>) => {
    if (mousePressed) {
      const deltaY = event.clientY - origin[1];
      setPercent(Math.round(deltaY * 1.5) % 100);
    }
  };

  let color = colors.normal;
  if (pressed) {
    color = control ? colors.control : colors.pressed;
  }
  return (
    <div style={{ textAlign: 'center', padding: '.4rem' }} onMouseDown={onMouseDown} onMouseUp={onMouseUp} onMouseMove={onMouseMove}>
      <svg width="4rem" height="4rem" viewBox="0 0 20 20" version="1.1">
        <g transform={`rotate(${(percent * 360) / 100})`} style={{ transformOrigin: 'center' }}>
          <circle fill={colors.normal} fillRule="evenodd" stroke="#a10000" strokeWidth=".5" strokeOpacity="1" cx="10" cy="10" r="9" />
          <circle fill={color} fillRule="evenodd" cx="10" cy="10" r="4" />
          <circle fill="#000000" cx="10" cy="4" r="2" />
        </g>
        <text alignmentBaseline="middle" textAnchor="middle" x="10" y="10" className="knob">
          {k.keybind}
        </text>
      </svg>
      <div style={{ fontSize: '.8rem' }}>{k.label}</div>
      <div style={{ fontSize: '.8rem' }}>{k.alt_label}&nbsp;</div>
    </div>
  );
}
