import Note from '../Note'
import Scale from './Scale'

const zip = rows=>rows[0].map((_,c)=>rows.map(row=>row[c]))

const Chord = (name) => {
  const chords = {
    major: ['1', '3', '5'],
    major_seventh: ['1', '3', '5', '7'],
    seventh: ['1', '3', '5', '7-'],
    minor: ['1', '3-', '5'],
    minor_seventh: ['1', '3-', '5', '7'],
    augmented: ['1', '3', '5+'],
    half_diminished_seventh: ['1', '3-', '5-', '7-'],
    diminished: ['1', '3-', '5-'],
    diminished_seventh: ['1', '3-', '5-', '7--'],
    seventh_aug_fifth: ['1', '3', '5+', '7-'],
    seventh_dim_fifth: ['1', '3', '5-', '7-'],
    minor_major_seventh: ['1', '-3', '5', '7'],
    major_seventh_aug_fifth: ['1', '3', '5+', '7'],
    major_seventh_dim_fifth: ['1', '3', '5-', '7'],
    suspended_fourth: ['1', '3', '4'],
    seventh_suspended_fourth: ['1', '3', '4', '7'],
    sixth: ['1', '3', '5', '6'],
    minor_sixth: ['1', '3-', '5', '6'],
    ninth: ['1', '3', '5', '7-', '9'],
    major_ninth: ['1', '3', '5', '7', '9'],
    minor_ninth: ['1', '3-', '5', '7-', '9'],
  }

  if (!name in chords) {
    throw `unknown chord name ${name}`
  }

  function notes(root) {
    let scale_notes = Scale('major').notes(root)
    return chords[name].map((interval, count) => {
      const minus = interval.split('-').length - 1
      const plus = interval.split('+').length - 1
      const mod = plus - minus
      return scale_notes[interval].add(mod)
    })
  }

  return Object.freeze({
    name, notes
  })
}

export default Chord