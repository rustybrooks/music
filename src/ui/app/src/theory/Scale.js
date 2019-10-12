import Note from '../Note.js'

const Scale = (name) => {
  const scales = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "natural_minor": [2, 1, 2, 2, 1, 2, 2],
    "harmonic_minor": [2, 1, 2, 2, 1, 3, 1],
    "melodic_minor": [2, 1, 2, 2, 2, 2, 1],
    "hungarian_minor, ": [2, 1, 3, 1, 1, 3, 1],
    "neapolitan_minor": [1, 2, 2, 2, 2, 2, 1],
    "neapolitan_major": [1, 2, 2, 2, 2, 2, 1],
    "pentatonic_major": [2, 2, 3, 2, 3, ],
    "pentatonic_minor": [3, 2, 2, 3, 2, ],
    "whole_tone": [2, 2, 2, 2, 2, 2, ],
    "diminished": [2, 1, 2, 1, 2, 1, 2, 1],
    "enigmatic": [1, 3, 2, 2, 2, 1, 1],
    "chromatic": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "ionian": [2, 2, 1, 2, 2, 2, 1],
    "dorian": [2, 1, 2, 2, 2, 1, 2],
    "phrygian": [1, 2, 2, 2, 1, 2, 2],
    "lydian": [2, 2, 2, 1, 2, 2, 1],
    "mixolydian": [2, 2, 1, 2, 2, 1, 2],
    "aeolian": [2, 1, 2, 2, 1, 2, 2],
    "aeoliant": [1, 2, 2, 1, 2, 2, 2],
  }

  if (!name in scales) {
    throw `unknown scale name ${name}`
  }

  function notes(root) {
    let this_note = Note(root)
    return scales[name].map((interval) => {
      this_note = this_note.add(interval)  // FIXME kinda gross
      return this_note
    })
  }

  return Object.freeze(
    {
      name, notes,
    }
  )
}

export default Scale