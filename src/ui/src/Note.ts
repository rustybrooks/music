const note_list = {
  sharp: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
  flat: ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
}

let x = 2;

interface NoteType {
    note: string,
    octave: number,
}

function note_to_number(n : NoteType) {
  const {note, octave} = n
  let i = note_list.sharp.indexOf(note.toUpperCase())
  if (i === -1) {
    i = note_list.flat.indexOf(note.toUpperCase())
  }

  return 36 + octave*12 + i
}

function number_to_note(n : number, is_sharp : boolean) {
  return {
    note: note_list[is_sharp ? 'sharp' : 'flat'][n % 12],
    octave: Math.trunc((n-36) / 12)
  };
}


const Note = (n : NoteType | number, is_sharp=true) => {
  function add(i : number) {
    return Note(number + i, is_sharp)
  }

  let number : number = null
  let note : NoteType = null

  if (typeof n == "number") {
    number = n
    note = number_to_note(n, is_sharp)
  } else {
    number = note_to_number(n)
    note = n
  }

  return Object.freeze({note, number, add})
}

export default Note
