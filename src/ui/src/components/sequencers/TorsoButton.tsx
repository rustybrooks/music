export enum ButtonState {
  inactive,
  active,
  passive,
  secondary,
  whiteActive,
  whiteInactive,
  blackActive,
  blackInactive,
}

const colors = {
  [ButtonState.inactive]: '#999',
  [ButtonState.active]: '#FF9',
  [ButtonState.passive]: '#bd9',
  [ButtonState.secondary]: '#F99',
  [ButtonState.whiteActive]: '#ffdddd',
  [ButtonState.whiteInactive]: '#eee',
  [ButtonState.blackActive]: '#997777',
  [ButtonState.blackInactive]: '#444444',
};

export function TorsoButton({
  b,
  onMouseDown = () => {},
  onMouseUp = () => {},
  row,
  col,
  state,
  text = '',
}: {
  b: any;
  row: number;
  col: number;
  onMouseDown?: (r: number, c: number) => void;
  onMouseUp?: (r: number, c: number) => void;
  state: ButtonState;
  text?: string;
}) {
  if (!b.length) {
    return <div style={{ width: '4rem' }} />;
  }

  return (
    <div className="torso-button" onMouseDown={() => onMouseDown(row, col)} onMouseUp={() => onMouseUp(row, col)}>
      <svg width="4rem" height="4rem" viewBox="0 0 20 20" version="1.1" style={{ margin: 0, padding: 0 }}>
        <rect fill={colors[state]} width="15.5" height="15.5" x="0.25" y="0.25" stroke="#666" strokeWidth=".5" strokeOpacity="1" />
        <text alignmentBaseline="middle" textAnchor="middle" x="8" y="8" className="button-label">
          {text.length ? text : b[2]}
        </text>
        <text x="2" y="19.25" className="button-bot">
          {b[0]}
        </text>
        <text alignmentBaseline="middle" transform="rotate(-90) translate(-11, 17.5)" className="button-side">
          {b[1]}
        </text>
      </svg>
    </div>
  );
}
