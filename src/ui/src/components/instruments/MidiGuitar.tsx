/*
import MidiMonitor from '../MidiMonitor';
import MidiInputs from '../MidiInputs';
import { Note, NoteType } from '../../lib/Note';

// import * as exercises from '../../exercises/guitar'

const tunings: { [id: string]: NoteType[] } = {
  guitar: [
    ['E', 0],
    ['A', 0],
    ['D', 1],
    ['G', 1],
    ['B', 1],
    ['E', 2],
  ],
};

// seems kind of dumb, but maybe some configurations will result in different channels
const channels = [0, 1, 2, 3, 4, 5];

const magic = 0.9438;

// const style = theme => {
function styleFn() {
  const x: any = {
    fretboard: {
      display: 'flex',
      width: '100%',
      height: '200px',
    },
    nut: {
      display: 'flex',
      width: '100%',
      height: '100%',
      'flex-flow': 'column',
    },
    fretboard2: {
      display: 'flex',
      width: '100%',
      height: '100%',
    },
    position: {
      display: 'flex',
      'flex-flow': 'column',
      height: '100%',
    },
    marker: {
      display: 'flex',
      'flex-flow': 'column',
      height: '100%',
      '-webkit-box-pack': 'center',
      'justify-content': 'center',
      '-webkit-box-align': 'center',
      'align-items': 'center',
    },
    fret: {
      display: 'flex',
      '-webkit-box-pack': 'center',
      'justify-content': 'center',
      '-webkit-box-align': 'center',
      'align-items': 'center',
      width: '100%',
      height: '100%',
    },
    fret2: {
      display: 'flex',
      '-webkit-box-pack': 'center',
      'justify-content': 'center',
      '-webkit-box-align': 'center',
      'align-items': 'center',
      height: '80%',
      width: '94%',
      margin: '10% 3%',
      'border-width': '1px',
      'border-style': 'solid',
      'border-color': 'darkgrey',
      'border-image': 'initial',
      'border-radius': '3px',
    },
    fretSelect: {},
  };

  x.pressBlank = { ...x.fret2, 'background-color': '#eee' };
  x.press = { ...x.fret2, 'background-color': '#66F' };
  x.pressError = { ...x.fret2, 'background-color': '#F66' };

  x.selectBlank = { ...x.fretSelect, 'background-color': '#eee' };
  x.select = { ...x.fretSelect, 'background-color': '#3A9' };

  return x;
}

const style = styleFn();

interface MidiGuitarProps {
  classes: any;
  tuning: string;
  frets: any;
  handed: any;
}

export const MidiGuitar = ({ classes, tuning, frets, handed }: MidiGuitarProps) => {
  tuning = tuning === undefined ? 'guitar' : tuning;
  frets = frets === undefined ? 17 : frets;
  handed = handed === undefined ? 'right' : handed;
  const notes = tunings[tuning].map(n => new Note(n)).reverse();

  // const exercise = exercises.FindNotes(notes, [Note(["A", 0])])

  const midi_callback = (m: any) => {
    if (!fretboard) {
      console.log('no fretboard');
      return;
    }

    let string = -1;
    let fret = 0;

    // this is a silly thing to let me pretend that 3 rows of launchpad buttons are the low 3 strings on guitar
    if (m.channel === 0 && m.note < 40) {
      if (m.note >= 0 && m.note <= 8) {
        string = 0;
        fret = handed === 'right' ? m.note : 8 - m.note;
      } else if (m.note >= 16 && m.note <= 24) {
        string = 1;
        fret = handed === 'right' ? m.note - 16 : 24 - m.note;
      } else if (m.note >= 32 && m.note <= 40) {
        string = 2;
        fret = handed === 'right' ? m.note - 32 : 40 - m.note;
      }
    } else {
      string = channels.findIndex(m.channel);
      fret = m.note - notes[string].number;
    }

    // console.log(string, fret)
    if (string < 0) return;

    const fret_events = exercise.callback(string, fret, m.command === m.NOTEON);

    const nf = fretboard.splice(0);

    fret_events.forEach((e: any) => {
      // console.log("event", e)
      if (e[0] === 'set_press') {
        const nfs = nf[string].slice(0);
        nfs[fret].pressed = ['press', 'error'].includes(e[1]);
        nfs[fret].error = e[1] === 'error';
        // console.log('set_press', nfs[fret].pressed, nfs[fret].error)
      }
    });

    setFretboard(nf);
  };

  let [fretboard, setFretboard] = React.useState(() => init_fretboard());

  function init_fretboard() {
    console.log('before init fret');
    const frets = 25;
    return [...Array(6)].map(() => {
      return [...Array(frets + 1)].map(() => {
        return {
          pressed: false,
          error: false,
          selected: false,
        };
      });
    });
  }

  function fret(f: number) {
    let width = 100;
    if (f) {
      // width = 5
      width = 12 * magic ** f;
    }
    return (
      <div style={{ width: `${width}%` }} className={classes.position} key={f}>
        {notes.map((n: any, i: number) => {
          const fs = fretboard[i][f];

          return (
            <div key={n.number} className={classes.fret}>
              <div className={classes[fs.pressed ? (fs.error ? 'pressError' : 'press') : 'pressBlank']}>
                <div className={classes[fs.selected ? 'select' : fs.pressed ? '' : 'selectBlank']}>
                  {n.add(f).note} / {n.add(f).number}
                </div>
              </div>
            </div>
          );
        })}
        <div className={classes.marker}>{f}</div>
      </div>
    );
  }

  function first(left = false) {
    const w = 10;
    const x = left ? 100 - w : 0;
    return (
      <svg key="first" width={`${w}%`} height="100%" x={`${x}%`} y="0">
        <foreignObject width="100%" height="100%">
          <div className={classes.nut}>{fret(0)}</div>
        </foreignObject>
      </svg>
    );
  }

  function rest(left = false) {
    const w = 89.25;
    const x = left ? 100 - 10.75 - w : 10.75;
    return (
      <svg key="rest" width={`${w}%`} height="100%" x={`${x}%`} y="0">
        <foreignObject width="100%" height="100%">
          <div className={classes.fretboard2}>{// [...Array(frets).keys()].map(f => fret(left ? frets-f : f+1)) }</div>
        </foreignObject>
      </svg>
    );
  }

  function nut(left = false) {
    const w = 0.75;
    const x = left ? 100 - 10 - w : 10;
    return (
      <svg key="nut" width={`${w}%`} height="100%" x={`${x}%`} y="0">
        <rect x="5%" y="2%" rx="3" ry="3" width="90%" height="96%" fill="lightgray" stroke="none" />
      </svg>
    );
  }

  function stuff() {
    // return [rest(handed==='left'), nut(handed==='left'), first(handed==='left')]
    return [first(handed === 'left'), nut(handed === 'left'), rest(handed === 'left')];
  }

  return (
    <div>
      <div className={classes.fretboard}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
          stroke="black"
          strokeWidth="1"
          fill="white"
          shapeRendering="geometricPrecision"
          style={{ overflow: 'visible' }}
        >
          {stuff()}
        </svg>
      </div>
      <MidiMonitor />
      <MidiInputs callback={midi_callback} />
    </div>
  );
};

*/
