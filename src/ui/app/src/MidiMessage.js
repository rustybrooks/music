const NOTEON = 'NoteOn'
const NOTEOFF = 'NoteOff'

const MidiMessage = (m) => {
  let command = null
  let [dcommand, note, velocity] = m.data

  const midi_event = dcommand >> 4
  const channel = dcommand & 0xF

  console.log({dcommand, midi_event, channel, note, velocity})

  switch (midi_event) {
    case 8:
      if (velocity > 0) {
        command = NOTEON
      } else {
        command = NOTEOFF
      }
      break
    case 9:
      command = NOTEOFF
      break
    default:
      command = midi_event
  }

  return Object.freeze(
    {channel, command, note, velocity}
  )
}
export default MidiMessage
