const note_list = {
  sharp: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
  flat: ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
}

function note_to_number(n) {
  const [note, octave] = n
  let i = note_list.sharp.indexOf(note.toUpperCase())
  if (i === -1) {
    i = note_list.flat.indexOf(note.toUpperCase())
  }

  return 36 + octave*12 + i
}

function number_to_note(n, is_sharp) {
  return [note_list[is_sharp ? 'sharp' : 'flat'][n % 12], Math.trunc((n-36) / 12)]
}

const Note = (n, is_sharp = true) => {
  function add(i) {
    return Note(number + i, is_sharp)
  }

  let number = null
  let note = null

  if (Array.isArray(n)) {
    number = note_to_number(n)
    note = n
  } else {
    number = n
    note = number_to_note(n, is_sharp)
  }


  return Object.freeze({note, number, add})
}

export default Note
