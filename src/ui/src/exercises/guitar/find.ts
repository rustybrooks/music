// variations
// 1. order does not matter - show 'correct' note which might stay around for a file?
// 1a. duplication matters - incorrect if we've already done it
// 2. order does matter - show correct note if correct, otherwise show incorrect note.  goes away when unpressed

export const FindNotes = (tuning: any, notes: any, order_matters = false, octave_matters = false) => {
  // let score = 0
  // let hits = []

  function callback(string: number, fret: number, is_press: boolean) {
    // console.log(string, fret, is_press)
    if (!is_press) {
      return [['set_press', 'blank']];
    }

    const note = tuning[string].add(fret);

    let match_notes = [];
    if (!order_matters) {
      match_notes = notes;
    }

    // console.log('match_notes', match_notes)
    const matches = match_notes.filter((e: any) => {
      // console.log('filter', e.note[0], note.note[0])
      return octave_matters ? e.number === note.number : e.note[0] === note.note[0];
    });
    // console.log('matches', matches)
    if (matches.length) {
      return [['set_press', 'press']];
    }
    return [['set_press', 'error']];
  }

  function display() {}

  return Object.freeze({
    callback,
    display,
  });
};
