const note_list = {
  sharp: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
  flat: ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
}

type NoteType = [string, number];

function note_to_number(n : NoteType) {
  const [note, octave] = n
  let i = note_list.sharp.indexOf(note.toUpperCase())
  if (i === -1) {
    i = note_list.flat.indexOf(note.toUpperCase())
  }

  return 36 + octave*12 + i
}

function number_to_note(n : number, is_sharp : boolean) : NoteType {
  return [
    note_list[is_sharp ? 'sharp' : 'flat'][n % 12],
    Math.trunc((n-36) / 12)
  ]
}


class Note {
  number = 0;
  note : NoteType = null
  is_sharp = true

  add(i : number) {
    return new Note(this.number + i, this.is_sharp)
  }

  constructor(note: NoteType);
  constructor(num: number, is_sharp : boolean);
  constructor(n : any, is_sharp : any = true) {
    this.is_sharp = is_sharp
    if (typeof n == "number") {
      this.number = n
      this.note = number_to_note(n, is_sharp)
    } else {
      this.number = note_to_number(n)
      this.note = n
    }
  }
}

export { Note, NoteType }
