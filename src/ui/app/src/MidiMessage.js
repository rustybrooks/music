
const MidiMessage = (m) => {
  const NOTEON = 'NoteOn'
  const NOTEOFF = 'NoteOff'

  let [note, command, channel, velocity] = [null, null, null, null]
  const [b1, b2, b3] = m.data

  const mevent = b1 >> 4

  console.log("mevent", mevent)
  switch (mevent) {
    case 0x9:
      channel = b1 & 0xF
      note = b2
      velocity = b3
      if (velocity > 0) {
        command = NOTEON
        note = b2
      } else {
        command = NOTEOFF
      }
      break
    case 0x8:
      channel = b1 & 0xF
      note = b2
      velocity = b3
      command = NOTEOFF
      break
    case 0xA:
      // Polyphonic Key Pressure (Aftertouch)
      break
    case 0xB:
      // Control Change
      break
    case 0xC:
      // Program Change
      break
    case 0xD:
      // Channel Pressure (Aftertouch)
      break
    case 0xE:
      // Pitch Wheel
      break
    default:
      command = mevent  // Should probably just throw exception
  }

  console.log({mevent, b1, channel, note, velocity, command})

  return Object.freeze(
    {channel, command, note, velocity, NOTEON, NOTEOFF}
  )
}
export default MidiMessage

