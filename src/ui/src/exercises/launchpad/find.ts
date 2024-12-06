import { Note } from '../../lib/Note';

export const FindNotes = (_tuning: any, _notes: any, _order_matters = false, _octave_matters = false) => {
  // const score = 0;
  // const hits = [];

  function callback(_x: number, _y: number, _note: Note, is_press: boolean) {
    // console.log(string, fret, is_press)
    if (!is_press) {
      return [['set_press', 'blank']];
    }

    // const note = tuning[string].add(fret)
    //
    // let match_notes = []
    // if (order_matters) {
    //
    // } else {
    //   match_notes = notes
    // }
    //
    // // console.log('match_notes', match_notes)
    // let matches = match_notes.filter(e => {
    //   // console.log('filter', e.note[0], note.note[0])
    //   return octave_matters ? e.number === note.number : e.note[0] === note.note[0]
    // })
    // // console.log('matches', matches)
    // if (matches.length) {
    //   return [['set_press', 'press']]
    // } else {
    //   return [['set_press', 'error']]
    // }

    return [['set_press', 'press']];
  }

  // function display() {}

  return Object.freeze({
    callback,
  });
};
