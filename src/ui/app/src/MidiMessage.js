const MidiMessage = (m) => {
  let [command, note, velocity] = [null, null,  null]
  let [dcommand, dnote, dvelocity] = m.data

  console.log(dcommand, dnote, dvelocity)

  switch (dcommand) {
    case 176:  // I dunno
      break
    case 144:
      if (dvelocity > 0) {
        command = 'NoteOn'
        note = dnote
        velocity = dvelocity
      } else {
        command = 'NoteOff'
        note = dnote
      }
      break
    case 128:
      command = 'NoteOff'
      note = dnote
      break
  }

  return Object.freeze(
    {command, note, velocity}
  )
}
export default MidiMessage